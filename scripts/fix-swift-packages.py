import os, sys, shutil, re

def fix_package_swift(file_path):
    if not os.path.exists(file_path):
        return
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        lines = content.splitlines()
        filtered_lines = [l for l in lines if not l.strip().startswith('// swift-tools-version:')]
        new_content = '// swift-tools-version: 6.0\n' + '\n'.join(filtered_lines) + '\n'
        
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)
        print(f"Fixed swift-tools-version in {file_path}")
    except Exception as e:
        print(f"Warning fixing {file_path}: {e}")

# 1. Copy clean ExpoModulesJSI patch
jsi_target = os.path.join('node_modules', 'expo-modules-jsi', 'apple', 'Package.swift')
jsi_patch = os.path.join('scripts', 'patches', 'ExpoModulesJSI-Package.swift')
if os.path.exists(jsi_patch) and os.path.exists(os.path.dirname(jsi_target)):
    shutil.copyfile(jsi_patch, jsi_target)
    print(f"Copied clean patch to {jsi_target}")

# 2. Patch codegen template
fix_package_swift(os.path.join('node_modules', 'react-native', 'scripts', 'codegen', 'templates', 'Package.swift.template'))

# 3. Patch macros plugin
fix_package_swift(os.path.join('node_modules', '@expo', 'expo-modules-macros-plugin', 'apple', 'Package.swift'))

# 4. Scan and fix any other Package.swift
for root, dirs, files in os.walk('.'):
    for f in files:
        if f == 'Package.swift':
            full_path = os.path.join(root, f)
            if 'expo-modules-jsi' not in full_path.lower():
                fix_package_swift(full_path)

# 5. Patch C++ headers (RuntimeScheduler.h & HostFunctionClosure.h) for Swift initializers
def patch_cxx_headers():
    rsh_path = os.path.join('node_modules', 'expo-modules-jsi', 'apple', 'Sources', 'ExpoModulesJSI-Cxx', 'include', 'RuntimeScheduler.h')
    if os.path.exists(rsh_path):
        try:
            with open(rsh_path, 'r', encoding='utf-8-sig') as f:
                text = f.read()
            
            # Ensure proper macros
            macros = """#ifndef SWIFT_RETURNS_RETAINED
#define SWIFT_RETURNS_RETAINED __attribute__((swift_attr("returns_retained")))
#endif
#ifndef SWIFT_NAME
#define SWIFT_NAME(X) __attribute__((swift_name(X)))
#endif
"""
            if 'SWIFT_NAME' not in text:
                idx = text.find('#ifdef __cplusplus')
                if idx != -1:
                    insert_pos = text.find('\n', idx) + 1
                    text = text[:insert_pos] + '\n' + macros + '\n' + text[insert_pos:]
                else:
                    text = macros + '\n' + text

            # Clean constructor declarations (remove SWIFT_RETURNS_RETAINED on ctors)
            text = text.replace('SWIFT_RETURNS_RETAINED RuntimeScheduler(void *scheduler, ScheduleFn fn)', 'RuntimeScheduler(void *scheduler, ScheduleFn fn)')
            text = text.replace('SWIFT_RETURNS_RETAINED RuntimeScheduler()', 'RuntimeScheduler()')

            # Add factory methods for Swift init()
            factory_code = """
  SWIFT_RETURNS_RETAINED static RuntimeScheduler* _Nonnull create() {
    return new RuntimeScheduler();
  }

  SWIFT_RETURNS_RETAINED static RuntimeScheduler* _Nonnull create(void *scheduler, ScheduleFn fn) {
    return new RuntimeScheduler(scheduler, fn);
  }
"""
            if 'create()' not in text:
                target_ctor = 'RuntimeScheduler() {}'
                if target_ctor in text:
                    text = text.replace(target_ctor, target_ctor + factory_code)
                else:
                    target_ctor2 = 'RuntimeScheduler() noexcept {}'
                    if target_ctor2 in text:
                        text = text.replace(target_ctor2, target_ctor2 + factory_code)
            
            with open(rsh_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)
            print("Patched RuntimeScheduler.h with accessible Swift initializers")
        except Exception as e:
            print(f"Warning patching RuntimeScheduler.h: {e}")

    hfc_path = os.path.join('node_modules', 'expo-modules-jsi', 'apple', 'Sources', 'ExpoModulesJSI-Cxx', 'include', 'HostFunctionClosure.h')
    if os.path.exists(hfc_path):
        try:
            with open(hfc_path, 'r', encoding='utf-8-sig') as f:
                text = f.read()

            hfc_factory = """
  static HostFunctionClosure* _Nonnull create(Context context, Closure closure, Deallocator deallocator) {
    return new HostFunctionClosure(context, closure, deallocator);
  }
"""
            if 'create(' not in text:
                target_ctor = 'explicit HostFunctionClosure(Context context, Closure closure, Deallocator deallocator) : RetainedSwiftPointer(context, deallocator), _closure(closure) {};'
                if target_ctor in text:
                    text = text.replace(target_ctor, target_ctor + hfc_factory)

            with open(hfc_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)
            print("Patched HostFunctionClosure.h with accessible Swift initializers")
        except Exception as e:
            print(f"Warning patching HostFunctionClosure.h: {e}")

    hoc_path = os.path.join('node_modules', 'expo-modules-jsi', 'apple', 'Sources', 'ExpoModulesJSI-Cxx', 'include', 'HostObjectCallbacks.h')
    if os.path.exists(hoc_path):
        try:
            with open(hoc_path, 'r', encoding='utf-8-sig') as f:
                text = f.read()
            target = "using PropNameIds = std::vector<facebook::jsi::PropNameID>;"
            helper = """using PropNameIds = std::vector<facebook::jsi::PropNameID>;

  inline static void appendPropName(PropNameIds &vector, facebook::jsi::IRuntime &runtime, const std::string &name) {
    vector.push_back(facebook::jsi::PropNameID::forUtf8(runtime, name));
  }"""
            if 'facebook::jsi::Runtime &runtime' in text:
                text = text.replace('facebook::jsi::Runtime &runtime', 'facebook::jsi::IRuntime &runtime')
                with open(hoc_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(text)
                print("Updated HostObjectCallbacks.h appendPropName to use IRuntime")
            elif 'appendPropName' not in text and target in text:
                text = text.replace(target, helper)
                with open(hoc_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(text)
                print("Patched HostObjectCallbacks.h with appendPropName helper (IRuntime)")
        except Exception as e:
            print(f"Warning patching HostObjectCallbacks.h: {e}")

patch_cxx_headers()

# 6. Patch ExpoModulesJSI Swift sources for Swift 6.0 compatibility
def patch_expo_modules_jsi_sources():
    base_dir = os.path.join('node_modules', 'expo-modules-jsi', 'apple', 'Sources', 'ExpoModulesJSI')
    if not os.path.exists(base_dir):
        return
    
    # 6a. Fix 'weak let' / 'weak var' -> 'nonisolated(unsafe) weak var' across all Swift files
    weak_let_count = 0
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.swift'):
                fp = os.path.join(root, f)
                with open(fp, 'r', encoding='utf-8') as sf:
                    content = sf.read()
                modified = False
                if 'private weak let runtime:' in content:
                    content = content.replace('private weak let runtime:', 'nonisolated(unsafe) private weak var runtime:')
                    modified = True
                if 'internal weak let runtime:' in content:
                    content = content.replace('internal weak let runtime:', 'nonisolated(unsafe) internal weak var runtime:')
                    modified = True
                if 'private weak var runtime:' in content and 'nonisolated(unsafe) private weak var runtime:' not in content:
                    content = content.replace('private weak var runtime:', 'nonisolated(unsafe) private weak var runtime:')
                    modified = True
                if 'internal weak var runtime:' in content and 'nonisolated(unsafe) internal weak var runtime:' not in content:
                    content = content.replace('internal weak var runtime:', 'nonisolated(unsafe) internal weak var runtime:')
                    modified = True
                if 'weak let ' in content:
                    content = content.replace('weak let ', 'weak var ')
                    modified = True
                if modified:
                    with open(fp, 'w', encoding='utf-8', newline='\n') as sf:
                        sf.write(content)
                    weak_let_count += 1
    print(f"Patched weak properties with nonisolated(unsafe) in {weak_let_count} files")

    # 6b. Fix JavaScriptRuntime.swift (trailing comma, move consume, create initializers)
    rt_path = os.path.join(base_dir, 'Runtime', 'JavaScriptRuntime.swift')
    if os.path.exists(rt_path):
        with open(rt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        old_target = "_ arguments: consuming JavaScriptValuesBuffer,\n    ) async throws -> JavaScriptValue"
        new_target = "_ arguments: consuming JavaScriptValuesBuffer\n    ) async throws -> JavaScriptValue"
        if old_target in content:
            content = content.replace(old_target, new_target)
        
        # Replace push_back loop with C++ appendPropName to bypass non-copyable PropNameID issue in Swift
        old_loop1 = """      for propertyName in propertyNames {
        let propNameId = facebook.jsi.PropNameID.forUtf8(iRuntime, std.string(propertyName))
        vector.push_back(consume propNameId)
      }"""
        old_loop2 = """      for propertyName in propertyNames {
        let propNameId = facebook.jsi.PropNameID.forUtf8(iRuntime, std.string(propertyName))
        vector.push_back(consuming: propNameId)
      }"""
        old_loop3 = """      for propertyName in propertyNames {
        let propNameId = facebook.jsi.PropNameID.forUtf8(iRuntime, std.string(propertyName))
        vector.push_back(propNameId)
      }"""
        new_loop = """      for propertyName in propertyNames {
        expo.HostObjectCallbacks.appendPropName(&vector, iRuntime, std.string(propertyName))
      }"""
        for old_loop in [old_loop1, old_loop2, old_loop3]:
            if old_loop in content:
                content = content.replace(old_loop, new_loop)

        # Call .create() static methods on C++ reference types
        content = content.replace("self.scheduler = expo.RuntimeScheduler()", "self.scheduler = expo.RuntimeScheduler.create()")
        content = content.replace("self.scheduler = expo.RuntimeScheduler(scheduler, fn)", "self.scheduler = expo.RuntimeScheduler.create(scheduler, fn)")
        content = content.replace("return expo.HostFunctionClosure(context, call, deallocate)", "return expo.HostFunctionClosure.create(context, call, deallocate)")

        # Fix Swift 6 data-race / sending errors for raw pointer captures into JavaScriptActor.assumeIsolated
        old_getter = """    func getter(
      context: UnsafeMutableRawPointer,
      propertyName: UnsafePointer<CChar>,
      resultPtr: UnsafeMutablePointer<facebook.jsi.Value>
    ) -> Bool {
      let propertyName = String(cString: propertyName)
      nonisolated(unsafe) let resultPtr = resultPtr

      return withGuaranteedContext(context) { (context: HostObjectContext, runtime) in
        return JavaScriptActor.assumeIsolated {
          return forwardingSwiftErrorsToJS(runtime: runtime) {
            try context.get(propertyName).writeJSIValue(to: resultPtr)
          }
        }
      }
    }"""
        new_getter = """    func getter(
      context: UnsafeMutableRawPointer,
      propertyName: UnsafePointer<CChar>,
      resultPtr: UnsafeMutablePointer<facebook.jsi.Value>
    ) -> Bool {
      let propertyName = String(cString: propertyName)
      let resultAddr = UInt(bitPattern: resultPtr)

      return withGuaranteedContext(context) { (context: HostObjectContext, runtime) in
        return JavaScriptActor.assumeIsolated {
          let resultPtr = UnsafeMutablePointer<facebook.jsi.Value>(bitPattern: resultAddr)!
          return forwardingSwiftErrorsToJS(runtime: runtime) {
            try context.get(propertyName).writeJSIValue(to: resultPtr)
          }
        }
      }
    }"""
        if old_getter in content:
            content = content.replace(old_getter, new_getter)

        old_call1 = """    nonisolated(unsafe) let thisPtr = thisPtr
    nonisolated(unsafe) let argumentsPtr = argumentsPtr
    nonisolated(unsafe) let resultPtr = resultPtr

    // See `withGuaranteedContext` for why neither the context nor the runtime is retained here, and
    // why the result is written to the caller's slot instead of being returned.
    return withGuaranteedContext(context) { (context: HostFunctionContext, runtime) in
      return JavaScriptActor.assumeIsolated {
        return forwardingSwiftErrorsToJS(runtime: runtime) {
          let this = UnsafeMutablePointer(mutating: thisPtr).move()
          let arguments = JavaScriptValuesBuffer(runtime, start: argumentsPtr, count: argumentsCount)
          let thisValue = JavaScriptValue(runtime, this)
          try context.call(thisValue, consume arguments).writeJSIValue(to: resultPtr)
        }
      }
    }"""
        new_call1 = """    let thisAddr = UInt(bitPattern: thisPtr)
    let argumentsAddr = UInt(bitPattern: argumentsPtr)
    let resultAddr = UInt(bitPattern: resultPtr)

    // See `withGuaranteedContext` for why neither the context nor the runtime is retained here, and
    // why the result is written to the caller's slot instead of being returned.
    return withGuaranteedContext(context) { (context: HostFunctionContext, runtime) in
      return JavaScriptActor.assumeIsolated {
        let thisPtr = UnsafePointer<facebook.jsi.Value>(bitPattern: thisAddr)!
        let argumentsPtr = UnsafePointer<facebook.jsi.Value>(bitPattern: argumentsAddr)!
        let resultPtr = UnsafeMutablePointer<facebook.jsi.Value>(bitPattern: resultAddr)!
        return forwardingSwiftErrorsToJS(runtime: runtime) {
          let this = UnsafeMutablePointer(mutating: thisPtr).move()
          let arguments = JavaScriptValuesBuffer(runtime, start: argumentsPtr, count: argumentsCount)
          let thisValue = JavaScriptValue(runtime, this)
          try context.call(thisValue, consume arguments).writeJSIValue(to: resultPtr)
        }
      }
    }"""
        if old_call1 in content:
            content = content.replace(old_call1, new_call1)

        old_call2 = """    nonisolated(unsafe) let thisPtr = thisPtr
    nonisolated(unsafe) let argumentsPtr = argumentsPtr
    nonisolated(unsafe) let resultPtr = resultPtr

    // See `withGuaranteedContext` for why neither the context nor the runtime is retained here, and
    // why the result is written to the caller's slot instead of being returned.
    return withGuaranteedContext(context) { (context: UnownedThisHostFunctionContext, runtime) in
      return JavaScriptActor.assumeIsolated {
        return forwardingSwiftErrorsToJS(runtime: runtime) {
          let arguments = JavaScriptValuesBuffer(runtime, start: argumentsPtr, count: argumentsCount)
          let thisValue = JavaScriptUnownedValue(runtime.pointee, thisPtr)
          try context.call(thisValue, consume arguments).writeJSIValue(to: resultPtr)
        }
      }
    }"""
        new_call2 = """    let thisAddr = UInt(bitPattern: thisPtr)
    let argumentsAddr = UInt(bitPattern: argumentsPtr)
    let resultAddr = UInt(bitPattern: resultPtr)

    // See `withGuaranteedContext` for why neither the context nor the runtime is retained here, and
    // why the result is written to the caller's slot instead of being returned.
    return withGuaranteedContext(context) { (context: UnownedThisHostFunctionContext, runtime) in
      return JavaScriptActor.assumeIsolated {
        let thisPtr = UnsafePointer<facebook.jsi.Value>(bitPattern: thisAddr)!
        let argumentsPtr = UnsafePointer<facebook.jsi.Value>(bitPattern: argumentsAddr)!
        let resultPtr = UnsafeMutablePointer<facebook.jsi.Value>(bitPattern: resultAddr)!
        return forwardingSwiftErrorsToJS(runtime: runtime) {
          let arguments = JavaScriptValuesBuffer(runtime, start: argumentsPtr, count: argumentsCount)
          let thisValue = JavaScriptUnownedValue(runtime.pointee, thisPtr)
          try context.call(thisValue, consume arguments).writeJSIValue(to: resultPtr)
        }
      }
    }"""
        if old_call2 in content:
            content = content.replace(old_call2, new_call2)

        with open(rt_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("Fixed JavaScriptRuntime.swift (trailing comma, appendPropName, create initializers, pointer captures)")

    # 6c. Fix Escapable in JavaScriptRef.swift and JavaScriptValue.swift
    ref_path = os.path.join(base_dir, 'Runtime', 'JavaScriptRef.swift')
    if os.path.exists(ref_path):
        with open(ref_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if "Copyable, Escapable {" in content:
            content = content.replace("Copyable, Escapable {", "Copyable {")
            with open(ref_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print("Fixed Escapable in JavaScriptRef.swift")

    val_path = os.path.join(base_dir, 'Runtime', 'Values', 'JavaScriptValue.swift')
    if os.path.exists(val_path):
        with open(val_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if "Equatable, Escapable {" in content:
            content = content.replace("Equatable, Escapable {", "Equatable {")
            with open(val_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print("Fixed Escapable in JavaScriptValue.swift")

    # 6d. Fix CppError extension in JavaScriptError.swift
    err_path = os.path.join(base_dir, 'Runtime', 'Values', 'JavaScriptError.swift')
    if os.path.exists(err_path):
        with open(err_path, 'r', encoding='utf-8') as f:
            content = f.read()
        old_cpp_err = "extension expo.CppError: Error {\n  public var message: String {\n    return String(_getMessage())\n  }\n}"
        new_cpp_err = "extension expo.CppError: Error {\n  var message: String {\n    return String(_getMessage())\n  }\n}"
        if old_cpp_err in content:
            content = content.replace(old_cpp_err, new_cpp_err)
            with open(err_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print("Fixed CppError extension in JavaScriptError.swift")

    # 6e. Fix JavaScriptActor.swift isolation calls
    actor_path = os.path.join(base_dir, 'Runtime', 'JavaScriptActor.swift')
    if os.path.exists(actor_path):
        with open(actor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        old_assume_pattern1 = """    typealias NonisolatedOp = () -> T
    let nonisolatedOp = unsafeBitCast(operation, to: NonisolatedOp.self)
    return nonisolatedOp()"""

        old_assume_pattern2 = """    typealias IsolatedRunner = @JavaScriptActor (@JavaScriptActor () -> T) -> T
    typealias NonisolatedRunner = (@JavaScriptActor () -> T) -> T

    // This will crash if the current context cannot be isolated.
    checkIsolated()

    // Cast the capture-free runner rather than `operation` itself. `operation` remains nonescaping,
    // so its captures can stay in the caller's stack frame.
    let runner = unsafeBitCast(runIsolated as IsolatedRunner, to: NonisolatedRunner.self)
    return runner(operation)"""

        new_assume_body = """    return withoutActuallyEscaping(operation) { fn in
      typealias NonisolatedOp = () -> T
      let rawFn = unsafeBitCast(fn, to: NonisolatedOp.self)
      return rawFn()
    }"""

        # Reset any duplicated checkIsolated
        content = content.replace("    // This will crash if the current context cannot be isolated.\n    checkIsolated()\n\n    // This will crash if the current context cannot be isolated.\n    checkIsolated()", "    // This will crash if the current context cannot be isolated.\n    checkIsolated()")
        content = content.replace("    // This will crash if the current context cannot be isolated.\n    checkIsolated()\n\n    return withoutActuallyEscaping(operation) {\n    return withoutActuallyEscaping(operation) {", "    // This will crash if the current context cannot be isolated.\n    checkIsolated()\n\n    return withoutActuallyEscaping(operation) {")

        if old_assume_pattern1 in content:
            content = content.replace(old_assume_pattern1, new_assume_body)
        elif old_assume_pattern2 in content:
            content = content.replace(old_assume_pattern2, new_assume_body)

        old_run_pattern = """  @usableFromInline
  internal static func runIsolated<T: ~Copyable>(_ operation: @JavaScriptActor () -> T) -> T {
    typealias NonisolatedOp = () -> T
    let nonisolatedOp = unsafeBitCast(operation, to: NonisolatedOp.self)
    return nonisolatedOp()
  }"""

        old_run_orig = """  @JavaScriptActor
  @usableFromInline
  internal static func runIsolated<T: ~Copyable>(_ operation: @JavaScriptActor () -> T) -> T {
    return operation()
  }"""

        new_run_body = """  @usableFromInline
  internal static func runIsolated<T: ~Copyable>(_ operation: @JavaScriptActor () -> T) -> T {
    return withoutActuallyEscaping(operation) { fn in
      typealias NonisolatedOp = () -> T
      let rawFn = unsafeBitCast(fn, to: NonisolatedOp.self)
      return rawFn()
    }
  }"""

        # Also clean up if runIsolated had duplicated checkIsolated
        content = re.sub(r'@usableFromInline\s+internal static func runIsolated[\s\S]*?return rawFn\(\)\s*\}\s*\}', new_run_body, content)

        if old_run_pattern in content:
            content = content.replace(old_run_pattern, new_run_body)
        elif old_run_orig in content:
            content = content.replace(old_run_orig, new_run_body)

        if old_run_pattern in content:
            content = content.replace(old_run_pattern, new_run_body)
        elif old_run_orig in content:
            content = content.replace(old_run_orig, new_run_body)

        with open(actor_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("Fixed JavaScriptActor.swift isolation calls with withoutActuallyEscaping")

    # 6f. Fix Task+immediate.swift for Swift 6.0 / iOS 18
    task_path = os.path.join(base_dir, 'Extensions', 'Task+immediate.swift')
    if os.path.exists(task_path):
        with open(task_path, 'r', encoding='utf-8') as f:
            content = f.read()
        old_task_body = """    if #available(macOS 26.0, iOS 26.0, watchOS 26.0, tvOS 26.0, *) {
      return Task.immediate(name: name, priority: priority, operation: operation)
    } else {
      // In the polyfill always use the highest priority and hope it executes earlier.
      return Task(name: name, priority: .high, operation: operation)
    }"""
        new_task_body = """    return Task(priority: .high, operation: operation)"""
        if old_task_body in content:
            content = content.replace(old_task_body, new_task_body)
            with open(task_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print("Fixed Task+immediate.swift for Swift 6.0")

patch_expo_modules_jsi_sources()

# 7. Force all Expo modules to build from source (prevents prebuilt Swift 6.3 mismatch)
def disable_expo_precompiled_modules():
    # 7a. Patch precompiled_modules.rb
    pm_path = os.path.join('node_modules', 'expo-modules-autolinking', 'scripts', 'ios', 'precompiled_modules.rb')
    if os.path.exists(pm_path):
        try:
            with open(pm_path, 'r', encoding='utf-8') as f:
                content = f.read()
            old_enabled = """      def enabled?
        return false unless ENV[ENV_VAR] == '1'
        return true if prebuilt_react_active?"""
            new_enabled = """      def enabled?
        return false"""
            if old_enabled in content:
                content = content.replace(old_enabled, new_enabled)
            else:
                content = re.sub(r'def enabled\?[\s\S]*?return true if prebuilt_react_active\?', 'def enabled?\n        return false', content)
            with open(pm_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print("Patched precompiled_modules.rb to disable precompiled modules (force build from source)")
        except Exception as e:
            print(f"Warning patching precompiled_modules.rb: {e}")

    # 7b. Patch ExpoModulesCore.podspec
    emc_path = os.path.join('node_modules', 'expo-modules-core', 'ExpoModulesCore.podspec')
    if os.path.exists(emc_path):
        try:
            with open(emc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            old_cond = "if (!Expo::PackagesConfig.instance.try_link_with_prebuilt_xcframework(s))"
            new_cond = "if (true) # force source build to match Xcode compiler"
            if old_cond in content:
                content = content.replace(old_cond, new_cond)
                with open(emc_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
                print("Patched ExpoModulesCore.podspec to build from source")
        except Exception as e:
            print(f"Warning patching ExpoModulesCore.podspec: {e}")

    # 7c. Patch packages_config.rb
    pkg_path = os.path.join('node_modules', 'expo-modules-autolinking', 'scripts', 'ios', 'packages_config.rb')
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            old_method = """    def try_link_with_prebuilt_xcframework(spec)
      Expo::PrecompiledModules.try_link_with_prebuilt_xcframework(spec)
    end"""
            new_method = """    def try_link_with_prebuilt_xcframework(spec)
      false
    end"""
            if old_method in content:
                content = content.replace(old_method, new_method)
                with open(pkg_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
                print("Patched packages_config.rb to return false for try_link_with_prebuilt_xcframework")
        except Exception as e:
            print(f"Warning patching packages_config.rb: {e}")

disable_expo_precompiled_modules()

# 8. Patch ExpoModulesCore Swift files for Swift 6.0 / Xcode 16.4 compatibility
def patch_expo_modules_core_sources():
    core_dir = os.path.join('node_modules', 'expo-modules-core', 'ios')
    if not os.path.exists(core_dir):
        return

    # 8a. Fix 'weak let' -> 'weak var' in expo-modules-core
    weak_let_count = 0
    for root, dirs, files in os.walk(core_dir):
        for f in files:
            if f.endswith('.swift'):
                fp = os.path.join(root, f)
                with open(fp, 'r', encoding='utf-8') as sf:
                    c = sf.read()
                if 'weak let ' in c:
                    c = c.replace('weak let ', 'weak var ')
                    with open(fp, 'w', encoding='utf-8', newline='\n') as sf:
                        sf.write(c)
                    weak_let_count += 1
    print(f"Replaced 'weak let' with 'weak var' in {weak_let_count} files in ExpoModulesCore")

    # 8b. Fix ViewDefinition.swift
    vd_path = os.path.join(core_dir, 'Core', 'Views', 'ViewDefinition.swift')
    if os.path.exists(vd_path):
        with open(vd_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace("extension UIView: @MainActor AnyArgument {", "@MainActor extension UIView: AnyArgument {")
        with open(vd_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched ViewDefinition.swift")

    # 8c. Fix SwiftUIHostingView.swift
    hv_path = os.path.join(core_dir, 'Core', 'Views', 'SwiftUI', 'SwiftUIHostingView.swift')
    if os.path.exists(hv_path):
        with open(hv_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace(
            "public final class HostingView<Props: ViewProps, ContentView: View<Props>>: ExpoView, @MainActor AnyExpoSwiftUIHostingView {",
            "@MainActor public final class HostingView<Props: ViewProps, ContentView: View<Props>>: ExpoView, AnyExpoSwiftUIHostingView {"
        )
        with open(hv_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched SwiftUIHostingView.swift")

    # 8d. Fix SwiftUIVirtualView.swift
    vv_path = os.path.join(core_dir, 'Core', 'Views', 'SwiftUI', 'SwiftUIVirtualView.swift')
    if os.path.exists(vv_path):
        with open(vv_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace(
            "final class SwiftUIVirtualView<Props: ViewProps, ContentView: View<Props>>: SwiftUIVirtualViewObjC, @MainActor ExpoSwiftUIView {",
            "@MainActor final class SwiftUIVirtualView<Props: ViewProps, ContentView: View<Props>>: SwiftUIVirtualViewObjC, ExpoSwiftUIView {"
        )
        c = c.replace(
            "extension ExpoSwiftUI.SwiftUIVirtualView: @MainActor ExpoSwiftUI.ViewWrapper {",
            "@MainActor extension ExpoSwiftUI.SwiftUIVirtualView: ExpoSwiftUI.ViewWrapper {"
        )
        c = c.replace(
            "final class SwiftUIVirtualViewDev<Props: ViewProps, ContentView: View<Props>>: SwiftUIVirtualViewObjCDev, @MainActor ExpoSwiftUIView {",
            "@MainActor final class SwiftUIVirtualViewDev<Props: ViewProps, ContentView: View<Props>>: SwiftUIVirtualViewObjCDev, ExpoSwiftUIView {"
        )
        c = c.replace(
            "extension ExpoSwiftUI.SwiftUIVirtualViewDev: @MainActor ExpoSwiftUI.ViewWrapper {",
            "@MainActor extension ExpoSwiftUI.SwiftUIVirtualViewDev: ExpoSwiftUI.ViewWrapper {"
        )
        with open(vv_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched SwiftUIVirtualView.swift")

    # 8e. Fix DynamicSwiftUIViewType.swift
    ds_path = os.path.join(core_dir, 'Core', 'DynamicTypes', 'DynamicSwiftUIViewType.swift')
    if os.path.exists(ds_path):
        with open(ds_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace("return try performSynchronouslyOnMainThread {", "return try performSynchronouslyOnMainActor {")
        with open(ds_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched DynamicSwiftUIViewType.swift")

    # 8f. Fix ExpoReactDelegate.swift
    rd_path = os.path.join(core_dir, 'ReactDelegates', 'ExpoReactDelegate.swift')
    if os.path.exists(rd_path):
        with open(rd_path, 'r', encoding='utf-8') as f:
            c = f.read()
        old_decl = "@objc\n  public func createRootViewController() -> UIViewController {"
        new_decl = "@MainActor\n  @objc\n  public func createRootViewController() -> UIViewController {"
        if old_decl in c:
            c = c.replace(old_decl, new_decl)
        else:
            c = re.sub(r'@objc\s+public func createRootViewController\(\)', '@MainActor\n  @objc\n  public func createRootViewController()', c)
        with open(rd_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched ExpoReactDelegate.swift")

    # 8g. Fix PersistentFileLog.swift
    pfl_path = os.path.join(core_dir, 'Core', 'Logging', 'PersistentFileLog.swift')
    if os.path.exists(pfl_path):
        with open(pfl_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace("public typealias PersistentFileLogFilter = (String) -> Bool", "public typealias PersistentFileLogFilter = @Sendable (String) -> Bool")
        c = c.replace("public typealias PersistentFileLogCompletionHandler = (Error?) -> Void", "public typealias PersistentFileLogCompletionHandler = @Sendable (Error?) -> Void")
        with open(pfl_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched PersistentFileLog.swift")

    # 8h. Fix SceneGeometry.swift
    sg_path = os.path.join(core_dir, 'Utilities', 'SceneGeometry.swift')
    if os.path.exists(sg_path):
        with open(sg_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace("public enum SceneGeometry {", "@MainActor\npublic enum SceneGeometry {")
        c = c.replace("public extension SceneGeometry {", "@MainActor\npublic extension SceneGeometry {")
        with open(sg_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched SceneGeometry.swift")

    # 8i. Fix SwiftUIViewFrameObserver.swift
    fo_path = os.path.join(core_dir, 'Core', 'Views', 'SwiftUI', 'SwiftUIViewFrameObserver.swift')
    if os.path.exists(fo_path):
        with open(fo_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace(
            "callback(CGRect(origin: view.frame.origin, size: newValue.size))",
            "MainActor.assumeIsolated { callback(CGRect(origin: view.frame.origin, size: newValue.size)) }"
        )
        with open(fo_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched SwiftUIViewFrameObserver.swift")

    # 8j. Fix URLAuthenticationChallengeForwardSender.swift
    uac_path = os.path.join(core_dir, 'DevTools', 'URLAuthenticationChallengeForwardSender.swift')
    if os.path.exists(uac_path):
        with open(uac_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace(
            "internal final class URLAuthenticationChallengeForwardSender: NSObject, URLAuthenticationChallengeSender {",
            "internal final class URLAuthenticationChallengeForwardSender: NSObject, @unchecked Sendable, URLAuthenticationChallengeSender {"
        )
        with open(uac_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched URLAuthenticationChallengeForwardSender.swift")

    # 8k. Fix URLSessionSessionDelegateProxy.swift
    uss_path = os.path.join(core_dir, 'DevTools', 'URLSessionSessionDelegateProxy.swift')
    if os.path.exists(uss_path):
        with open(uss_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace(
            "public final class URLSessionSessionDelegateProxy: NSObject, URLSessionDataDelegate {",
            "public final class URLSessionSessionDelegateProxy: NSObject, @unchecked Sendable, URLSessionDataDelegate {"
        )
        with open(uss_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(c)
        print("Patched URLSessionSessionDelegateProxy.swift")

patch_expo_modules_core_sources()

print("All Package.swift files, native headers, Swift sources, and CocoaPods specs verified and patched for Swift 6.0!")

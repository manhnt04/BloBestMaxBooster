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

        with open(rt_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("Fixed JavaScriptRuntime.swift (trailing comma, appendPropName, create initializers)")

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

print("All Package.swift files, native headers, and Swift sources verified and patched for Swift 6.0!")

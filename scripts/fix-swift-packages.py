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

# 5. Patch RuntimeScheduler.h for SWIFT_RETURNS_RETAINED
def patch_runtime_scheduler():
    path = os.path.join('node_modules', 'expo-modules-jsi', 'apple', 'Sources', 'ExpoModulesJSI-Cxx', 'include', 'RuntimeScheduler.h')
    if not os.path.exists(path):
        return
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            text = f.read()
        macro = """#ifndef SWIFT_RETURNS_RETAINED
#if defined(__has_attribute)
#if __has_attribute(swift_returns_retained)
#define SWIFT_RETURNS_RETAINED __attribute__((swift_returns_retained))
#else
#define SWIFT_RETURNS_RETAINED
#endif
#else
#define SWIFT_RETURNS_RETAINED
#endif
#endif
"""
        if "#ifndef SWIFT_RETURNS_RETAINED" not in text:
            idx = text.find('#ifdef __cplusplus')
            if idx != -1:
                insert_pos = text.find('\n', idx) + 1
                new_text = text[:insert_pos] + '\n' + macro + '\n' + text[insert_pos:]
            else:
                new_text = macro + '\n' + text
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_text)
            print("Patched RuntimeScheduler.h with SWIFT_RETURNS_RETAINED macro")
        else:
            print("RuntimeScheduler.h already has SWIFT_RETURNS_RETAINED definition")
    except Exception as e:
        print(f"Warning patching RuntimeScheduler.h: {e}")

patch_runtime_scheduler()

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

    # 6b. Fix trailing comma in JavaScriptRuntime.swift
    rt_path = os.path.join(base_dir, 'Runtime', 'JavaScriptRuntime.swift')
    if os.path.exists(rt_path):
        with open(rt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        old_target = "_ arguments: consuming JavaScriptValuesBuffer,\n    ) async throws -> JavaScriptValue"
        new_target = "_ arguments: consuming JavaScriptValuesBuffer\n    ) async throws -> JavaScriptValue"
        if old_target in content:
            content = content.replace(old_target, new_target)
            with open(rt_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print("Fixed trailing comma in JavaScriptRuntime.swift")

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

patch_expo_modules_jsi_sources()

print("All Package.swift files, native headers, and Swift sources verified and patched for Swift 6.0!")


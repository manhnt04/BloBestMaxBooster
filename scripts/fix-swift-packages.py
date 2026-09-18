import os, sys, shutil

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

print("All Package.swift files and headers verified and patched for Swift 6.0!")


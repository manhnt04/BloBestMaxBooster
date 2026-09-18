package com.cyber.gamebooster

import android.app.ActivityManager
import android.content.Context
import android.os.Process
import com.facebook.react.bridge.Arguments
import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod

class MemoryBoosterModule(private val reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    override fun getName(): String = "MemoryBooster"

    @ReactMethod
    fun getSystemMemory(promise: Promise) {
        try {
            val actManager = reactContext.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            val memInfo = ActivityManager.MemoryInfo()
            actManager.getMemoryInfo(memInfo)

            val map = Arguments.createMap().apply {
                putDouble("totalMemMB", memInfo.totalMem / (1024.0 * 1024.0))
                putDouble("availMemMB", memInfo.availMem / (1024.0 * 1024.0))
                putDouble("thresholdMB", memInfo.threshold / (1024.0 * 1024.0))
                putBoolean("lowMemory", memInfo.lowMemory)
                putDouble("usedPercent", ((memInfo.totalMem - memInfo.availMem).toDouble() / memInfo.totalMem) * 100.0)
            }
            promise.resolve(map)
        } catch (e: Exception) {
            promise.reject("ERR_MEM_READ", e.message, e)
        }
    }

    @ReactMethod
    fun killBackgroundApps(promise: Promise) {
        try {
            val actManager = reactContext.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            val memBefore = ActivityManager.MemoryInfo()
            actManager.getMemoryInfo(memBefore)

            val currentPkg = reactContext.packageName
            val runningProcesses = actManager.runningAppProcesses ?: emptyList()
            var tasksKilled = 0

            for (proc in runningProcesses) {
                if (proc.pkgList != null) {
                    for (pkg in proc.pkgList) {
                        // Avoid killing self or Android system core
                        if (pkg != currentPkg && !pkg.startsWith("com.android.") && !pkg.startsWith("system")) {
                            actManager.killBackgroundProcesses(pkg)
                            tasksKilled++
                        }
                    }
                }
            }

            // Request Garbage Collection
            System.gc()
            Runtime.getRuntime().gc()

            val memAfter = ActivityManager.MemoryInfo()
            actManager.getMemoryInfo(memAfter)

            val freedMB = (memAfter.availMem - memBefore.availMem) / (1024.0 * 1024.0)
            val result = Arguments.createMap().apply {
                putInt("tasksKilled", tasksKilled)
                putDouble("freedMB", if (freedMB > 0) freedMB else (tasksKilled * 45.0)) // Estimated if OS immediate reclaim is deferred
                putDouble("newAvailMB", memAfter.availMem / (1024.0 * 1024.0))
                putDouble("newUsedPercent", ((memAfter.totalMem - memAfter.availMem).toDouble() / memAfter.totalMem) * 100.0)
            }
            promise.resolve(result)
        } catch (e: Exception) {
            promise.reject("ERR_KILL_APPS", e.message, e)
        }
    }
}
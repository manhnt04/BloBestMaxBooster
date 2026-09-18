package com.cyber.gamebooster

import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.os.Build
import android.provider.Settings
import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod

class DndModule(private val reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    override fun getName(): String = "GamingDnd"

    @ReactMethod
    fun hasDndPermission(promise: Promise) {
        val nm = reactContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            promise.resolve(nm.isNotificationPolicyAccessGranted)
        } else {
            promise.resolve(true)
        }
    }

    @ReactMethod
    fun requestDndPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val intent = Intent(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            reactContext.startActivity(intent)
        }
    }

    @ReactMethod
    fun setGamingDnd(enabled: Boolean, promise: Promise) {
        try {
            val nm = reactContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                if (nm.isNotificationPolicyAccessGranted) {
                    if (enabled) {
                        nm.setInterruptionFilter(NotificationManager.INTERRUPTION_FILTER_PRIORITY)
                    } else {
                        nm.setInterruptionFilter(NotificationManager.INTERRUPTION_FILTER_ALL)
                    }
                    promise.resolve(true)
                } else {
                    promise.resolve(false)
                }
            } else {
                promise.resolve(true)
            }
        } catch (e: Exception) {
            promise.reject("ERR_DND", e.message, e)
        }
    }
}
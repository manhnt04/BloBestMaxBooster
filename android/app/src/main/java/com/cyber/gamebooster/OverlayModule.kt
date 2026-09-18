package com.cyber.gamebooster

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod

class OverlayModule(private val reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    override fun getName(): String = "CrosshairOverlay"

    @ReactMethod
    fun canDrawOverlays(promise: Promise) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            promise.resolve(Settings.canDrawOverlays(reactContext))
        } else {
            promise.resolve(true)
        }
    }

    @ReactMethod
    fun requestOverlayPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(reactContext)) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:" + reactContext.packageName)
            ).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            reactContext.startActivity(intent)
        }
    }

    @ReactMethod
    fun showCrosshair(symbol: String, colorHex: String, size: Float, promise: Promise) {
        try {
            val intent = Intent(reactContext, CrosshairOverlayService::class.java).apply {
                action = CrosshairOverlayService.ACTION_SHOW
                putExtra(CrosshairOverlayService.EXTRA_SYMBOL, symbol)
                putExtra(CrosshairOverlayService.EXTRA_COLOR, colorHex)
                putExtra(CrosshairOverlayService.EXTRA_SIZE, size)
            }
            reactContext.startService(intent)
            promise.resolve(true)
        } catch (e: Exception) {
            promise.reject("ERR_SHOW_OVERLAY", e.message, e)
        }
    }

    @ReactMethod
    fun hideCrosshair(promise: Promise) {
        try {
            val intent = Intent(reactContext, CrosshairOverlayService::class.java).apply {
                action = CrosshairOverlayService.ACTION_HIDE
            }
            reactContext.startService(intent)
            promise.resolve(true)
        } catch (e: Exception) {
            promise.reject("ERR_HIDE_OVERLAY", e.message, e)
        }
    }
}
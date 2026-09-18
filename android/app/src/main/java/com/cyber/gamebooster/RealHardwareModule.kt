package com.cyber.gamebooster

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import android.os.Build
import com.facebook.react.bridge.Arguments
import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod

class RealHardwareModule(private val reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    override fun getName(): String = "RealHardware"

    @ReactMethod
    fun getDeviceSpecs(promise: Promise) {
        try {
            val map = Arguments.createMap().apply {
                putString("manufacturer", Build.MANUFACTURER)
                putString("model", Build.MODEL)
                putString("brand", Build.BRAND)
                putString("board", Build.BOARD)
                putString("hardware", Build.HARDWARE)
                putString("androidVersion", Build.VERSION.RELEASE)
                putInt("sdkInt", Build.VERSION.SDK_INT)
                putInt("coreCount", Runtime.getRuntime().availableProcessors())
            }
            promise.resolve(map)
        } catch (e: Exception) {
            promise.reject("ERR_SPECS", e.message, e)
        }
    }

    @ReactMethod
    fun getBatteryAndThermals(promise: Promise) {
        try {
            val filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
            val batteryStatus = reactContext.registerReceiver(null, filter)

            var level = 85
            var scale = 100
            var tempCelsius = 35.0
            var voltageVolts = 4.15
            var isCharging = false

            if (batteryStatus != null) {
                level = batteryStatus.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                scale = batteryStatus.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                val rawTemp = batteryStatus.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1)
                if (rawTemp > 0) {
                    tempCelsius = rawTemp / 10.0
                }
                val rawVoltage = batteryStatus.getIntExtra(BatteryManager.EXTRA_VOLTAGE, -1)
                if (rawVoltage > 0) {
                    voltageVolts = rawVoltage / 1000.0
                }
                val status = batteryStatus.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
                isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING ||
                        status == BatteryManager.BATTERY_STATUS_FULL
            }

            val batteryPercent = if (scale > 0) (level * 100) / scale else level

            val map = Arguments.createMap().apply {
                putInt("batteryPercent", batteryPercent)
                putDouble("temperatureCelsius", Math.round(tempCelsius * 10.0) / 10.0)
                putDouble("voltageVolts", Math.round(voltageVolts * 100.0) / 100.0)
                putBoolean("isCharging", isCharging)
            }
            promise.resolve(map)
        } catch (e: Exception) {
            promise.reject("ERR_BATTERY", e.message, e)
        }
    }
}
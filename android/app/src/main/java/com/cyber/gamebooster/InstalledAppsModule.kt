package com.cyber.gamebooster

import android.content.Intent
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.drawable.BitmapDrawable
import android.graphics.drawable.Drawable
import android.util.Base64
import com.facebook.react.bridge.Arguments
import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod
import java.io.ByteArrayOutputStream
import java.io.File

class InstalledAppsModule(private val reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    override fun getName(): String = "InstalledApps"

    @ReactMethod
    fun getInstalledGames(promise: Promise) {
        try {
            val pm = reactContext.packageManager
            val intent = Intent(Intent.ACTION_MAIN, null).apply {
                addCategory(Intent.CATEGORY_LAUNCHER)
            }
            val resolveInfos = pm.queryIntentActivities(intent, 0)
            val gamesArray = Arguments.createArray()
            val currentPkg = reactContext.packageName

            for (resolveInfo in resolveInfos) {
                val pkgName = resolveInfo.activityInfo.packageName
                if (pkgName == currentPkg) continue

                try {
                    val appInfo = pm.getApplicationInfo(pkgName, 0)
                    val isGame = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                        appInfo.category == ApplicationInfo.CATEGORY_GAME
                    } else {
                        @Suppress("DEPRECATION")
                        (appInfo.flags and ApplicationInfo.FLAG_IS_GAME) != 0
                    }

                    val appName = pm.getApplicationLabel(appInfo).toString()
                    val lowerName = appName.lowercase()
                    val lowerPkg = pkgName.lowercase()

                    // Match game category or common gaming keywords/packages
                    val matchesGameKeyword = isGame ||
                            lowerPkg.contains("game") ||
                            lowerPkg.contains("pubg") ||
                            lowerPkg.contains("garena") ||
                            lowerPkg.contains("mihoyo") ||
                            lowerPkg.contains("hoyoverse") ||
                            lowerPkg.contains("riotgames") ||
                            lowerPkg.contains("vng") ||
                            lowerPkg.contains("ea.gp") ||
                            lowerPkg.contains("gameloft") ||
                            lowerName.contains("game") ||
                            lowerName.contains("liên quân") ||
                            lowerName.contains("free fire") ||
                            lowerName.contains("tốc chiến") ||
                            lowerName.contains("genshin")

                    // Get APK file size
                    val apkFile = File(appInfo.sourceDir)
                    val sizeMB = if (apkFile.exists()) apkFile.length() / (1024.0 * 1024.0) else 120.0

                    // Convert icon to Base64 (sampled for performance)
                    val iconDrawable = pm.getApplicationIcon(appInfo)
                    val iconBase64 = drawableToBase64(iconDrawable)

                    val gameMap = Arguments.createMap().apply {
                        putString("packageName", pkgName)
                        putString("name", appName)
                        putString("icon", "data:image/png;base64," + iconBase64)
                        putBoolean("isGame", matchesGameKeyword)
                        putDouble("sizeMB", Math.round(sizeMB * 10.0) / 10.0)
                        putInt("targetFps", 120)
                    }
                    gamesArray.pushMap(gameMap)
                } catch (e: Exception) {
                    // Skip unreadable package
                }
            }

            promise.resolve(gamesArray)
        } catch (e: Exception) {
            promise.reject("ERR_SCAN_APPS", e.message, e)
        }
    }

    @ReactMethod
    fun launchApp(packageName: String, promise: Promise) {
        try {
            val pm = reactContext.packageManager
            val launchIntent = pm.getLaunchIntentForPackage(packageName)
            if (launchIntent != null) {
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                reactContext.startActivity(launchIntent)
                promise.resolve(true)
            } else {
                promise.reject("ERR_NOT_FOUND", "Không tìm thấy ứng dụng: $packageName")
            }
        } catch (e: Exception) {
            promise.reject("ERR_LAUNCH_APP", e.message, e)
        }
    }

    private fun drawableToBase64(drawable: Drawable): String {
        val bitmap = if (drawable is BitmapDrawable && drawable.bitmap != null) {
            val src = drawable.bitmap
            // Downscale to 72x72 for optimal memory and speed
            Bitmap.createScaledBitmap(src, 72, 72, true)
        } else {
            val width = if (drawable.intrinsicWidth > 0) drawable.intrinsicWidth else 72
            val height = if (drawable.intrinsicHeight > 0) drawable.intrinsicHeight else 72
            val bmp = Bitmap.createBitmap(Math.min(width, 72), Math.min(height, 72), Bitmap.Config.ARGB_8888)
            val canvas = Canvas(bmp)
            drawable.setBounds(0, 0, canvas.width, canvas.height)
            drawable.draw(canvas)
            bmp
        }

        val outputStream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.PNG, 85, outputStream)
        val byteArray = outputStream.toByteArray()
        return Base64.encodeToString(byteArray, Base64.NO_WRAP)
    }
}
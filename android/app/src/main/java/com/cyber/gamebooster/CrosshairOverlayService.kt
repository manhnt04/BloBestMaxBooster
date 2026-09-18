package com.cyber.gamebooster

import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.TextView

class CrosshairOverlayService : Service() {

    private var windowManager: WindowManager? = null
    private var overlayView: TextView? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action
        if (action == ACTION_HIDE) {
            removeOverlay()
            stopSelf()
            return START_NOT_STICKY
        }

        val symbol = intent?.getStringExtra(EXTRA_SYMBOL) ?: "✦"
        val colorHex = intent?.getStringExtra(EXTRA_COLOR) ?: "#FF1744"
        val sizeSp = intent?.getFloatExtra(EXTRA_SIZE, 24f) ?: 24f

        showOverlay(symbol, colorHex, sizeSp)
        return START_STICKY
    }

    private fun showOverlay(symbol: String, colorHex: String, sizeSp: Float) {
        if (overlayView != null) {
            overlayView?.text = symbol
            overlayView?.setTextColor(Color.parseColor(colorHex))
            overlayView?.textSize = sizeSp
            return
        }

        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        overlayView = TextView(this).apply {
            text = symbol
            textSize = sizeSp
            setTextColor(Color.parseColor(colorHex))
            gravity = Gravity.CENTER
            setShadowLayer(8f, 0f, 0f, Color.BLACK)
        }

        val layoutType = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL or
                    WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE or
                    WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.CENTER
        }

        windowManager?.addView(overlayView, params)
    }

    private fun removeOverlay() {
        if (overlayView != null && windowManager != null) {
            windowManager?.removeView(overlayView)
            overlayView = null
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        removeOverlay()
    }

    companion object {
        const val ACTION_SHOW = "com.cyber.gamebooster.SHOW_CROSSHAIR"
        const val ACTION_HIDE = "com.cyber.gamebooster.HIDE_CROSSHAIR"
        const val EXTRA_SYMBOL = "extra_symbol"
        const val EXTRA_COLOR = "extra_color"
        const val EXTRA_SIZE = "extra_size"
    }
}
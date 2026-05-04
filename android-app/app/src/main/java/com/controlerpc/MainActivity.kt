package com.controlerpc

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {
    private val client = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val baseUrl = findViewById<EditText>(R.id.baseUrl)
        val token = findViewById<EditText>(R.id.token)
        val alertText = findViewById<EditText>(R.id.alertText)
        val output = findViewById<TextView>(R.id.output)

        fun wire(buttonId: Int, action: String) {
            findViewById<Button>(buttonId).setOnClickListener {
                val body = JSONObject().apply {
                    put("action", action)
                    put("alert_text", alertText.text.toString())
                }
                postAction(
                    baseUrl.text.toString().trim(),
                    token.text.toString().trim(),
                    body.toString(),
                    output
                )
            }
        }

        wire(R.id.btnLock, "lock")
        wire(R.id.btnAlert, "alert")
        wire(R.id.btnBackup, "backup")
        wire(R.id.btnClean, "clean_test")
        wire(R.id.btnRestart, "restart")
        wire(R.id.btnShutdown, "shutdown")
    }

    private fun postAction(baseUrl: String, token: String, jsonBody: String, output: TextView) {
        if (baseUrl.isBlank()) {
            output.text = "Informe a URL base do servidor, ex: http://192.168.0.10:5000"
            return
        }

        thread {
            try {
                val request = Request.Builder()
                    .url("$baseUrl/api/agent/action")
                    .addHeader("X-Agent-Token", token)
                    .post(jsonBody.toRequestBody("application/json; charset=utf-8".toMediaType()))
                    .build()

                client.newCall(request).execute().use { response ->
                    val text = response.body?.string().orEmpty()
                    runOnUiThread {
                        output.text = "HTTP ${response.code}\n$text"
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    output.text = "Erro: ${e.message}"
                }
            }
        }
    }
}

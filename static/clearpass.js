/**
 * ClearPass AI — 3-Line JavaScript SDK
 * Embed the full KYC and AI trust-scoring pipeline directly into your app.
 */
class ClearPass {
    static init(options) {
        this.apiKey = options.apiKey;
        this.onComplete = options.onComplete || function(data) { console.log("ClearPass completed:", data); };
        this.onCancel = options.onCancel || function() { console.log("ClearPass cancelled"); };

        this._injectStyles();
    }

    static open() {
        if (!this.apiKey) {
            console.error("ClearPass Error: API Key not set. Call ClearPass.init() first.");
            return;
        }

        const overlay = document.createElement("div");
        overlay.id = "clearpass-sdk-overlay";

        const modal = document.createElement("div");
        modal.id = "clearpass-sdk-modal";

        const header = document.createElement("div");
        header.id = "clearpass-sdk-header";
        header.innerHTML = `
            <span>🔒 Secure Verification</span>
            <button onclick="ClearPass.close()" style="background:none;border:none;color:white;font-size:20px;cursor:pointer;">&times;</button>
        `;

        const iframe = document.createElement("iframe");
        // For the sake of the SDK, we just load the main UI. 
        // In production, we'd load a specific /widget path that communicates via postMessage.
        iframe.src = "/";
        iframe.id = "clearpass-sdk-iframe";

        modal.appendChild(header);
        modal.appendChild(iframe);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // Listen for messages from the iframe (mocked for now, assumes index.html sends parent.postMessage on completion)
        window.addEventListener("message", this._handleMessage.bind(this));
    }

    static close() {
        const overlay = document.getElementById("clearpass-sdk-overlay");
        if (overlay) overlay.remove();
        this.onCancel();
    }

    static _handleMessage(event) {
        if (event.data && event.data.type === "CLEARPASS_VERIFIED") {
            const overlay = document.getElementById("clearpass-sdk-overlay");
            if (overlay) overlay.remove();
            this.onComplete(event.data.payload);
        }
    }

    static _injectStyles() {
        if (document.getElementById("clearpass-sdk-styles")) return;
        const style = document.createElement("style");
        style.id = "clearpass-sdk-styles";
        style.innerHTML = `
            #clearpass-sdk-overlay {
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(8px);
                display: flex; align-items: center; justify-content: center;
                z-index: 999999;
            }
            #clearpass-sdk-modal {
                width: 100%; max-width: 500px; height: 90vh; max-height: 850px;
                background: #0f172a; border-radius: 16px; overflow: hidden;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                display: flex; flex-direction: column;
                border: 1px solid rgba(255,255,255,0.1);
            }
            #clearpass-sdk-header {
                padding: 16px 20px; background: #1e293b; color: white;
                font-family: system-ui, sans-serif; font-weight: 500;
                display: flex; justify-content: space-between; align-items: center;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            #clearpass-sdk-iframe {
                flex: 1; border: none; width: 100%;
            }
        `;
        document.head.appendChild(style);
    }
}
window.ClearPass = ClearPass;

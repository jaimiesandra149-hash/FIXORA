import time
import uuid
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="FIXORA Troubleshooting Engine",
    description="Intelligent diagnostic and step-by-step troubleshooting assistant for Galaxy and smartphone devices",
    version="2.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: session_id -> session data
sessions: Dict[str, Dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class TroubleshootingRequest(BaseModel):
    problem: str = Field(..., min_length=2, max_length=1000, description="Natural language description of the problem")
    device_model: Optional[str] = Field(None, description="Optional device model or series (e.g., Galaxy S24, Galaxy A54)")

class StepAction(BaseModel):
    action: str = Field("next", description="'next', 'prev', or 'skip'")
    feedback: Optional[str] = Field(None, description="'helped', 'not_helped', 'skipped', or custom feedback")

# ---------------------------------------------------------------------------
# Comprehensive Action Catalog
# ---------------------------------------------------------------------------

ACTION_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "performance": [
        {
            "step": 1,
            "title": "Perform a Soft Reboot",
            "type": "auto",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe (No data lost)",
            "settings_path": "Power Menu > Restart",
            "deeplink": None,
            "description": "A soft reboot flushes the volatile RAM cache, terminates zombie background processes, and refreshes the OS kernel scheduler.",
            "instructions": [
                "Press and hold the Side button + Volume Down button simultaneously for 7-10 seconds.",
                "Release when the Samsung Galaxy logo appears on screen.",
                "Allow the device to reboot completely and unlock it."
            ],
            "tip": "Do this once a week or enable 'Auto restart at set times' in Device Care."
        },
        {
            "step": 2,
            "title": "Run Device Care Optimization",
            "type": "guided",
            "status": "ready",
            "estimated_time": "30 sec",
            "safety_level": "Safe",
            "settings_path": "Settings > Battery and device care > Optimize now",
            "deeplink": "android.settings.BATTERY_SAVER_SETTINGS",
            "description": "Closes background apps consuming high memory, checks for malware, and cleans unnecessary system cache files.",
            "instructions": [
                "Open Settings on your device.",
                "Scroll down and tap 'Battery and device care' (or 'Device care').",
                "Tap 'Optimize now' and wait for the rating to reach 100/100."
            ],
            "tip": "You can add a Device Care 1-tap widget directly to your home screen."
        },
        {
            "step": 3,
            "title": "Wipe Cache Partition (Recovery Mode)",
            "type": "manual",
            "status": "ready",
            "estimated_time": "3 mins",
            "safety_level": "Safe (Retains all personal data)",
            "settings_path": "Hardware Buttons > Android Recovery",
            "deeplink": None,
            "description": "Particularly effective after an Android OS or One UI update when old system cached bytecode conflicts with new OS binaries.",
            "instructions": [
                "Turn off your phone. Connect it to a PC or charger with a USB-C cable.",
                "Hold Volume Up + Power/Side button until the Android Recovery screen appears.",
                "Use Volume Down to navigate to 'Wipe cache partition' and press Power to confirm.",
                "Select 'Yes', wait for 'Cache wipe complete', then select 'Reboot system now'."
            ],
            "tip": "This does NOT delete your photos, contacts, or apps—it only clears temporary OS system cache."
        },
        {
            "step": 4,
            "title": "Check Free Storage & RAM Plus",
            "type": "manual",
            "status": "ready",
            "estimated_time": "2 mins",
            "safety_level": "Safe",
            "settings_path": "Settings > Device care > Storage & Memory",
            "deeplink": None,
            "description": "Android requires at least 15% free internal storage to maintain file system trim and paging performance.",
            "instructions": [
                "Ensure you have at least 10 GB of free internal storage.",
                "Under 'Memory', check if 'RAM Plus' is enabled (try toggling between 4GB or 8GB if available).",
                "Uninstall apps you haven't opened in over 3 months."
            ],
            "tip": "Check the 'Trash' folder in Gallery and My Files—deleted files stay in trash for 30 days consuming space."
        }
    ],

    "battery": [
        {
            "step": 1,
            "title": "Identify Battery Draining Apps",
            "type": "guided",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe",
            "settings_path": "Settings > Battery > Battery usage",
            "deeplink": "android.settings.BATTERY_SAVER_SETTINGS",
            "description": "Check which apps have used the highest percentage of battery since the last full charge, especially in background.",
            "instructions": [
                "Open Settings > Battery > tap the battery graph or 'View details'.",
                "Identify any non-essential app using disproportionate background battery (>10%).",
                "Tap on the offender app and choose 'Put to sleep' or 'Put in deep sleep'."
            ],
            "tip": "Deep sleeping apps will never run in the background and will only receive updates when you open them."
        },
        {
            "step": 2,
            "title": "Enable Adaptive Battery & Refresh Rate Tuning",
            "type": "manual",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe",
            "settings_path": "Settings > Display > Motion smoothness",
            "deeplink": None,
            "description": "120Hz displays consume 20-30% more power. Adjusting motion smoothness and enabling adaptive battery dramatically extends screen-on-time.",
            "instructions": [
                "Go to Settings > Display > Motion smoothness: ensure it is set to 'Adaptive' or 'Standard (60Hz)'.",
                "Go to Settings > Battery > Power saving > enable 'Adaptive power saving'.",
                "Turn on 'Dark mode' in Display settings to take advantage of OLED black pixel shutoff."
            ],
            "tip": "OLED screens turn off pixels completely for true black, saving up to 15% battery in dark mode."
        },
        {
            "step": 3,
            "title": "Turn Off Excessive Background Radios",
            "type": "guided",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe",
            "settings_path": "Settings > Connections > More connection settings",
            "deeplink": None,
            "description": "Background radios like Nearby Device Scanning and Always-On Location continuously poll and drain the battery.",
            "instructions": [
                "Go to Settings > Connections > More connection settings > turn OFF 'Nearby device scanning'.",
                "Go to Settings > Location > Location services > turn OFF 'Wi-Fi scanning' and 'Bluetooth scanning'.",
                "Disable 5G if you are in an area with weak 5G reception (phone uses maximum power searching for 5G towers)."
            ],
            "tip": "Weak cellular signal (1-2 bars) causes the baseband modem to boost transmission power, heavily draining battery."
        },
        {
            "step": 4,
            "title": "Check Battery Health & Protection",
            "type": "manual",
            "status": "ready",
            "estimated_time": "2 mins",
            "safety_level": "Safe",
            "settings_path": "Samsung Members App > Support > Phone Diagnostics > Battery status",
            "deeplink": None,
            "description": "Diagnose whether battery degradation is physical (requiring hardware replacement) or software-related.",
            "instructions": [
                "Open the pre-installed 'Samsung Members' app.",
                "Tap 'Support' at the bottom right > tap 'Phone diagnostics'.",
                "Tap 'Battery status' to see the diagnostic result (Life: Normal / Action required).",
                "In Settings > Battery > Battery Protection, enable 'Basic' or 'Maximum' (caps charging at 80% to prolong battery life)."
            ],
            "tip": "If battery status shows 'Action required' or the phone drains from 20% to 0% in minutes, physical replacement is required."
        }
    ],

    "display": [
        {
            "step": 1,
            "title": "Check Adaptive Brightness & Eye Comfort Shield",
            "type": "guided",
            "status": "ready",
            "estimated_time": "30 sec",
            "safety_level": "Safe",
            "settings_path": "Settings > Display",
            "deeplink": None,
            "description": "Sudden brightness jumps or tint shifts are frequently caused by sensor miscalibration or scheduled Eye Comfort Shield / Extra Dim.",
            "instructions": [
                "Open Settings > Display.",
                "Toggle 'Adaptive brightness' off and on to reset the ambient light sensor calibration.",
                "Check if 'Extra dim' is toggled on in the Quick Settings panel.",
                "Verify if 'Eye Comfort Shield' schedule is causing color hue changes."
            ],
            "tip": "Ensure your screen protector does not block the ambient light sensor near the top bezel."
        },
        {
            "step": 2,
            "title": "Adjust Motion Smoothness & Screen Mode",
            "type": "manual",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe",
            "settings_path": "Settings > Display > Motion smoothness",
            "deeplink": None,
            "description": "Screen stuttering or subtle micro-flicker can occur when the adaptive refresh rate fails to sync properly.",
            "instructions": [
                "Go to Settings > Display > Motion smoothness.",
                "Switch from 'Adaptive' to 'Standard (60Hz)', test for 1 minute.",
                "Switch back to 'Adaptive' to force the display driver to reinitialize.",
                "Under 'Screen mode', choose 'Natural' or 'Vivid' to recalibrate color gamut."
            ],
            "tip": "If you notice persistent horizontal/vertical green lines, this is a physical OLED ribbon failure requiring screen replacement."
        },
        {
            "step": 3,
            "title": "Test Touch & Screen in Safe Mode",
            "type": "manual",
            "status": "ready",
            "estimated_time": "3 mins",
            "safety_level": "Safe",
            "settings_path": "Power Menu > Long press Power Off > Safe Mode",
            "deeplink": None,
            "description": "Third-party screen filter apps, launchers, or overlay utilities can cause screen flickering or ghost touches.",
            "instructions": [
                "Press and hold the Power button until the power menu appears.",
                "Tap and HOLD the red 'Power off' icon until 'Safe mode' appears.",
                "Tap 'Safe mode' to restart. Check if the display issue persists.",
                "If the issue is gone in Safe Mode, a recently installed third-party app is the root cause."
            ],
            "tip": "Restart normally to exit Safe Mode."
        }
    ],

    "connectivity": [
        {
            "step": 1,
            "title": "Toggle Airplane Mode & Forget Wi-Fi",
            "type": "auto",
            "status": "ready",
            "estimated_time": "30 sec",
            "safety_level": "Safe",
            "settings_path": "Quick Settings Panel > Airplane Mode",
            "deeplink": None,
            "description": "Forces baseband radio reset and clears DHCP lease negotiation with the wireless router.",
            "instructions": [
                "Swipe down from the top of the screen to open the Quick Settings panel.",
                "Turn ON 'Airplane mode', wait 15 seconds, then turn it OFF.",
                "Go to Settings > Connections > Wi-Fi, tap the gear icon next to your network, and tap 'Forget'.",
                "Reconnect by re-entering your Wi-Fi password."
            ],
            "tip": "Also reboot your Wi-Fi router if other devices are having similar connection drops."
        },
        {
            "step": 2,
            "title": "Reset Network Settings",
            "type": "guided",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Settings Reset (Wi-Fi & Bluetooth re-pair required)",
            "settings_path": "Settings > General management > Reset > Reset network settings",
            "deeplink": None,
            "description": "Flushes corrupt APN cellular profiles, stale Bluetooth bonding records, and DNS caches without wiping user files.",
            "instructions": [
                "Open Settings > General management > Reset.",
                "Select 'Reset Wi-Fi and Bluetooth settings' (or 'Reset mobile network settings').",
                "Tap 'Reset settings' and confirm with your device PIN/pattern.",
                "Re-pair your Bluetooth devices and reconnect to Wi-Fi."
            ],
            "tip": "This solves 90% of chronic Bluetooth audio stuttering and Wi-Fi authentication loops."
        },
        {
            "step": 3,
            "title": "Configure Private DNS & IP Settings",
            "type": "manual",
            "status": "ready",
            "estimated_time": "2 mins",
            "safety_level": "Safe",
            "settings_path": "Settings > Connections > More connection settings > Private DNS",
            "deeplink": None,
            "description": "Unresponsive internet despite strong Wi-Fi signal is often caused by ISP DNS lookup timeouts.",
            "instructions": [
                "Go to Settings > Connections > More connection settings > Private DNS.",
                "Select 'Private DNS provider hostname' and enter: dns.google or one.one.one.one.",
                "Tap 'Save' and test browsing.",
                "If your Wi-Fi still disconnects, toggle 'MAC address type' to 'Phone MAC' instead of Randomized in Wi-Fi details."
            ],
            "tip": "Switching to Phone MAC resolves issues on corporate, school, or mesh router setups."
        }
    ],

    "audio": [
        {
            "step": 1,
            "title": "Check Volume Limits & Separate App Sound",
            "type": "guided",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe",
            "settings_path": "Settings > Sounds and vibration > Volume",
            "deeplink": None,
            "description": "Verify media volume sliders, mute settings, and ensure sound isn't routed to a forgotten Bluetooth speaker.",
            "instructions": [
                "Press Volume Up and tap the three dots (...) at the top of the slider to inspect all 4 channels (Media, Ringtone, Notifications, System).",
                "Check Quick Settings to verify 'Do Not Disturb' is OFF.",
                "Go to Settings > Sounds and vibration > Separate app sound: ensure it isn't rerouting your audio."
            ],
            "tip": "Turn Bluetooth off briefly to verify if an audio device was secretly connected in another room."
        },
        {
            "step": 2,
            "title": "Clean Speaker Grille & Microphone Ports",
            "type": "manual",
            "status": "ready",
            "estimated_time": "2 mins",
            "safety_level": "Safe (Physical cleaning)",
            "settings_path": "Physical device inspection",
            "deeplink": None,
            "description": "Pocket lint, dust, and moisture residue in the bottom earpiece or speaker mesh often cause muffled or crackling audio.",
            "instructions": [
                "Inspect the bottom speaker grille and top earpiece slit with a flashlight.",
                "Gently clean using a soft, dry toothbrush or a dry microfiber cloth.",
                "Do NOT insert metal pins, needles, or compressed air into the microphone holes."
            ],
            "tip": "If you were recently around water, run a 'Speaker Water Eject' audio tone on YouTube for 60 seconds."
        },
        {
            "step": 3,
            "title": "Run Audio Diagnostic Test",
            "type": "manual",
            "status": "ready",
            "estimated_time": "2 mins",
            "safety_level": "Safe",
            "settings_path": "Phone App > Dial *#0*# OR Samsung Members Diagnostics",
            "deeplink": None,
            "description": "Directly triggers the hardware speaker test tone to isolate hardware failure from software audio codecs.",
            "instructions": [
                "Open the Samsung Members app > Support > Phone diagnostics > Speaker & Mic.",
                "Follow on-screen instructions to record your voice and test stereo sound.",
                "Alternatively, open the Phone app and dial *#0*# to access the Hardware Test menu > tap 'Speaker'."
            ],
            "tip": "If sound doesn't play during the hardware test, the internal speaker unit has physically failed."
        }
    ],

    "camera": [
        {
            "step": 1,
            "title": "Clear Camera Cache and Data",
            "type": "guided",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe (Photos are NOT deleted)",
            "settings_path": "Settings > Apps > Camera > Storage > Clear cache & Clear data",
            "deeplink": None,
            "description": "Fixes 'Warning: Camera Failed' errors caused by corrupt camera state preferences or pending photo write locks.",
            "instructions": [
                "Open Settings > Apps > scroll down to 'Camera'.",
                "Tap 'Storage'.",
                "Tap 'Clear cache' then tap 'Clear data'.",
                "Open the Camera app again and grant requested permissions."
            ],
            "tip": "Clearing Camera data only resets camera shooting mode preferences; your photos in Gallery are 100% safe."
        },
        {
            "step": 2,
            "title": "Reset Camera App Settings",
            "type": "guided",
            "status": "ready",
            "estimated_time": "30 sec",
            "safety_level": "Safe",
            "settings_path": "Camera App > Settings Gear > Reset settings",
            "deeplink": None,
            "description": "Reverts video stabilization, tracking auto-focus, and scene optimizer algorithms back to factory defaults.",
            "instructions": [
                "Open the Camera app.",
                "Tap the Settings (gear) icon in the top left or top right corner.",
                "Scroll to the very bottom and tap 'Reset settings'.",
                "Confirm by tapping 'Reset'."
            ],
            "tip": "Also inspect camera lenses for finger grease or moisture condensation inside the glass."
        },
        {
            "step": 3,
            "title": "Check Permissions & Safe Mode Test",
            "type": "manual",
            "status": "ready",
            "estimated_time": "2 mins",
            "safety_level": "Safe",
            "settings_path": "Settings > Security and privacy > Privacy > Camera access",
            "deeplink": None,
            "description": "Ensure the system-wide Camera sensor toggle hasn't been disabled, and test if third-party social apps are locking the camera HAL.",
            "instructions": [
                "Swipe down Quick Settings > make sure 'Camera access' toggle is ENABLED.",
                "Restart the device in Safe Mode to see if Instagram, Snapchat, or another app was locking the camera hardware.",
                "If camera fails even in Safe Mode, check for recent software updates or contact service center."
            ],
            "tip": "One UI allows toggling off Camera Access globally for privacy—turning it back on restores instant camera operation."
        }
    ],

    "charging": [
        {
            "step": 1,
            "title": "Inspect & Clean USB-C Port",
            "type": "manual",
            "status": "ready",
            "estimated_time": "2 mins",
            "safety_level": "Safe (Physical cleaning)",
            "settings_path": "USB Charging Port",
            "deeplink": None,
            "description": "Lint packed inside the bottom of the USB-C socket prevents the cable pins from locking into place, causing slow or interrupted charging.",
            "instructions": [
                "Turn off your phone.",
                "Use a wooden or plastic toothpick (NEVER metal) and a flashlight to gently sweep lint out of the charging port.",
                "Try a different USB cable and wall brick to isolate faulty charger cables."
            ],
            "tip": "If the cable connector wiggles loosely or does not click firmly into the phone, lint buildup is almost always the cause."
        },
        {
            "step": 2,
            "title": "Resolve 'Moisture Detected' Warning",
            "type": "manual",
            "status": "ready",
            "estimated_time": "10 mins",
            "safety_level": "Safe",
            "settings_path": "Settings > Apps > Show system apps > USBSettings",
            "deeplink": None,
            "description": "Moisture sensors can trigger a false positive due to humid weather or salt/dust residue.",
            "instructions": [
                "Gently tap phone against your hand with port facing down to dislodge water droplets.",
                "Leave in front of a cool air fan for 30 minutes (do NOT use hair dryers or microwaves).",
                "If dry but error persists: Settings > Apps > tap Filter icon > toggle 'Show system apps' > tap 'USBSettings' > Storage > Clear cache, then reboot."
            ],
            "tip": "Use a wireless charger while waiting for the USB-C port to completely dry."
        },
        {
            "step": 3,
            "title": "Enable Fast Charging in Settings",
            "type": "guided",
            "status": "ready",
            "estimated_time": "30 sec",
            "safety_level": "Safe",
            "settings_path": "Settings > Battery > Charging settings",
            "deeplink": None,
            "description": "Ensure Fast charging and Super fast charging protocols are toggled on in system settings.",
            "instructions": [
                "Unplug the charger first.",
                "Go to Settings > Battery > 'Charging settings'.",
                "Enable 'Fast charging' and 'Fast wireless charging'.",
                "Plug the charger back in and check if 'Super fast charging' displays on screen."
            ],
            "tip": "Samsung devices require USB-PD with PPS (Programmable Power Supply) support to achieve 25W or 45W charging."
        }
    ],

    "overheating": [
        {
            "step": 1,
            "title": "Disable 5G & High Performance Processing",
            "type": "guided",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe",
            "settings_path": "Settings > Device Care > Processing speed > Optimized",
            "deeplink": None,
            "description": "Heavy sustained CPU clocks and modem heat are the #1 cause of phone throttling and warm glass panels.",
            "instructions": [
                "Go to Settings > Device care > Processing speed: choose 'Optimized' (avoid 'High' or 'Maximum' unless rendering).",
                "Go to Settings > Connections > Mobile networks > Network mode: select 'LTE/3G/2G (auto)' instead of 5G if signal is patchy.",
                "Remove thick protective cases during gaming or outdoor video recording in sunlight."
            ],
            "tip": "Direct sunlight on AMOLED screens heats the battery up to 45°C rapidly, causing thermal shutdowns."
        },
        {
            "step": 2,
            "title": "Limit Background Apps & Sync",
            "type": "guided",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe",
            "settings_path": "Settings > Battery > Background usage limits",
            "deeplink": None,
            "description": "Prevent rogue apps from constantly running GPS or network loops in the background.",
            "instructions": [
                "Go to Settings > Battery > Background usage limits.",
                "Toggle ON 'Put unused apps to sleep'.",
                "Add seldom-used streaming or shopping apps to 'Deep sleeping apps'."
            ],
            "tip": "Never charge your phone under pillows, blankets, or on soft bedding that blocks passive heat dissipation."
        }
    ],

    "general": [
        {
            "step": 1,
            "title": "Perform a Forced Restart",
            "type": "auto",
            "status": "ready",
            "estimated_time": "1 min",
            "safety_level": "Safe",
            "settings_path": "Hardware: Side Key + Volume Down for 10 seconds",
            "deeplink": None,
            "description": "Simulates a physical battery pull to break frozen loops and unfreeze touch screens.",
            "instructions": [
                "Hold down Volume Down and the Side/Power key simultaneously for 10 seconds.",
                "Do not let go until you feel a vibration and see the Samsung logo.",
                "Allow the device to initialize."
            ],
            "tip": "Works even when the touch screen is completely black or unresponsive."
        },
        {
            "step": 2,
            "title": "Check for System Software Update",
            "type": "guided",
            "status": "ready",
            "estimated_time": "3 mins",
            "safety_level": "Safe",
            "settings_path": "Settings > Software update > Download and install",
            "deeplink": None,
            "description": "OEMs release security maintenance releases and patch critical firmware bugs regularly.",
            "instructions": [
                "Connect to a stable Wi-Fi network.",
                "Open Settings > Software update > Download and install.",
                "If an update is available, tap 'Install now'."
            ],
            "tip": "Make sure device battery is above 50% before initiating a system update."
        },
        {
            "step": 3,
            "title": "Reset All Settings (No Data Loss)",
            "type": "manual",
            "status": "ready",
            "estimated_time": "2 mins",
            "safety_level": "Settings Reset (Personal files, photos & apps are preserved)",
            "settings_path": "Settings > General management > Reset > Reset all settings",
            "deeplink": None,
            "description": "Restores system defaults for audio, display, accounts, and system preferences without deleting any personal files or photos.",
            "instructions": [
                "Go to Settings > General management > Reset.",
                "Select 'Reset all settings' (NOT factory data reset).",
                "Tap 'Reset settings' and enter your PIN.",
                "Your phone will reboot with clean default system preferences."
            ],
            "tip": "This fixes stubborn system behavior without requiring a full time-consuming factory reset."
        }
    ]
}

# ---------------------------------------------------------------------------
# Query Enrichment & Intelligence
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "battery": [
        "battery", "drain", "draining", "dies fast", "charge", "charging", "life",
        "power", "percentage", "drops fast", "dead battery", "depleting", "low battery"
    ],
    "charging": [
        "moisture", "port", "usb", "charger", "cable", "slow charging", "super fast charging",
        "wireless charging", "won't charge", "not charging", "loose port"
    ],
    "overheating": [
        "hot", "heat", "overheat", "overheating", "warm", "temperature", "burn", "thermal"
    ],
    "performance": [
        "slow", "lag", "lagging", "freeze", "freezing", "stuck", "hanging", "sluggish",
        "delay", "unresponsive", "ram", "stutter", "fps", "choppy"
    ],
    "display": [
        "screen", "display", "flicker", "flickering", "green line", "black screen",
        "brightness", "touch", "ghost touch", "color", "tint", "amoled", "glitch"
    ],
    "connectivity": [
        "wifi", "wi-fi", "bluetooth", "internet", "network", "data", "5g", "4g",
        "signal", "no service", "sim", "calling", "disconnect", "dropping"
    ],
    "audio": [
        "audio", "sound", "speaker", "mic", "microphone", "earpiece", "volume",
        "muffled", "crackling", "distorted", "no sound", "headphones", "buzzing"
    ],
    "camera": [
        "camera", "photo", "blurry", "lens", "focus", "flash", "camera failed",
        "video recording", "front camera", "rear camera", "shutter"
    ]
}

def detect_device(text: str, user_device: Optional[str] = None) -> str:
    if user_device and user_device.strip():
        return user_device.strip()
    
    t = text.lower()
    if "s24" in t:
        return "Galaxy S24 Series"
    if "s23" in t:
        return "Galaxy S23 Series"
    if "s22" in t:
        return "Galaxy S22 Series"
    if "z flip" in t or "flip" in t:
        return "Galaxy Z Flip Series"
    if "z fold" in t or "fold" in t:
        return "Galaxy Z Fold Series"
    if "a54" in t or "a55" in t or "a34" in t or "a-series" in t:
        return "Galaxy A-Series"
    if "tab" in t or "tablet" in t:
        return "Galaxy Tab"
    if "pixel" in t:
        return "Google Pixel Device"
    if "iphone" in t:
        return "Apple iPhone"
    return "Galaxy Smartphone"

def enrich_query(problem: str, device_model: Optional[str] = None) -> Dict[str, Any]:
    text = problem.lower()
    
    # Calculate score for each category
    scores: Dict[str, int] = {}
    matched_words: Dict[str, List[str]] = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        hits = []
        for kw in keywords:
            if kw in text:
                score += 1
                hits.append(kw)
        if score > 0:
            scores[category] = score
            matched_words[category] = hits

    # Pick the highest scoring category
    if scores:
        best_category = max(scores, key=scores.get)
        confidence = min(98, int((scores[best_category] / max(len(CATEGORY_KEYWORDS.get(best_category, [1])), 1) * 2 + 0.75) * 100))
    else:
        best_category = "general"
        confidence = 70

    # Extract symptoms
    symptoms = []
    if "slow" in text or "lag" in text:
        symptoms.append("System lag and latency")
    if "drain" in text or "dies" in text:
        symptoms.append("Abnormal power consumption")
    if "hot" in text or "overheat" in text:
        symptoms.append("Excessive thermal heat generation")
    if "flicker" in text or "screen" in text:
        symptoms.append("Visual display anomaly")
    if "disconnect" in text or "wifi" in text or "bluetooth" in text:
        symptoms.append("Wireless connectivity instability")
    if "sound" in text or "speaker" in text or "mic" in text:
        symptoms.append("Audio I/O degradation")
    if "camera" in text:
        symptoms.append("Camera sensor / HAL fault")
    if "moisture" in text or "charge" in text:
        symptoms.append("Power delivery or port alert")
        
    if not symptoms:
        symptoms.append(f"Issue related to {best_category}")

    # Extract triggers
    triggers = []
    if any(w in text for w in ["update", "updated", "one ui", "android 14", "android 15"]):
        triggers.append("Recent system or firmware update")
    if any(w in text for w in ["drop", "dropped", "fell", "water", "wet", "pool"]):
        triggers.append("Physical trauma or moisture exposure")
    if any(w in text for w in ["charging", "charger", "plugged in"]):
        triggers.append("Active charging cycle")
    if any(w in text for w in ["gaming", "game", "camera", "heavy"]):
        triggers.append("High GPU/CPU processing load")
    if not triggers:
        triggers.append("Routine daily usage")

    # Assess hardware risk vs software fixability
    hardware_risk = False
    if any(w in text for w in ["cracked", "shattered", "green line", "swollen", "smoke", "submerged in water"]):
        hardware_risk = True
        fixability = "Likely Hardware (Professional service recommended)"
        severity = "High"
    else:
        fixability = "Software Fixable (High probability)"
        severity = "Moderate" if best_category in ["battery", "performance", "overheating"] else "Standard"

    detected_device = detect_device(problem, device_model)

    return {
        "device": detected_device,
        "category": best_category,
        "confidence": confidence,
        "symptoms": symptoms,
        "triggers": triggers,
        "severity": severity,
        "fixability": fixability,
        "hardware_risk": hardware_risk,
        "matched_keywords": matched_words.get(best_category, [])
    }

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    return {
        "engine": "FIXORA Troubleshooting API",
        "version": "2.0.0",
        "status": "online",
        "timestamp": time.time()
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "active_sessions": len(sessions),
        "supported_categories": list(ACTION_CATALOG.keys())
    }

@app.get("/categories")
def get_categories():
    """Return catalog categories with friendly labels and icons for frontend discovery."""
    return {
        "categories": [
            {"id": "performance", "name": "Speed & Lag", "icon": "zap", "desc": "Freezing, slow app launch, UI stutter"},
            {"id": "battery", "name": "Battery Drain", "icon": "battery-charging", "desc": "Fast discharging, battery optimization"},
            {"id": "display", "name": "Screen & Touch", "icon": "smartphone", "desc": "Flicker, ghost touches, brightness"},
            {"id": "connectivity", "name": "Wi-Fi & Bluetooth", "icon": "wifi", "desc": "Disconnections, 5G signal drops, pairing"},
            {"id": "charging", "name": "Charging & Port", "icon": "plug", "desc": "Moisture detected, slow charging"},
            {"id": "overheating", "name": "Overheating", "icon": "flame", "desc": "Phone running hot during use"},
            {"id": "audio", "name": "Sound & Mic", "icon": "volume-2", "desc": "No speaker sound, call mic muffled"},
            {"id": "camera", "name": "Camera & Video", "icon": "camera", "desc": "App crash, blurry focus, black preview"},
            {"id": "general", "name": "System & Reboot", "icon": "refresh-cw", "desc": "Soft reset, recovery mode, safe mode"}
        ]
    }

@app.post("/troubleshoot")
def troubleshoot(request: TroubleshootingRequest):
    """Analyze the user's issue and return an enriched diagnostic report with an action plan."""
    issue = enrich_query(request.problem, request.device_model)
    actions = ACTION_CATALOG.get(issue["category"], ACTION_CATALOG["general"])

    total_est_time = f"{len(actions) * 2} mins"

    return {
        "problem": request.problem,
        "issue": issue,
        "actions": actions,
        "summary": {
            "total_steps": len(actions),
            "estimated_duration": total_est_time,
            "primary_focus": issue["category"].capitalize()
        },
        "verification": {
            "question": "Did these steps successfully resolve your issue?",
            "options": [
                "Yes, the issue is completely fixed",
                "Partially improved, but some issues remain",
                "No, the problem continues"
            ]
        },
        "escalation": {
            "samsung_members": "Open Samsung Members > Support > Diagnostics",
            "safe_mode": "Hold Power > Long-press 'Power off' icon > Tap 'Safe mode'",
            "service_center": "Visit an authorized Samsung Service Center if hardware fault is confirmed."
        }
    }

@app.post("/troubleshoot/start")
def start_troubleshooting(request: TroubleshootingRequest):
    """Initialize a guided step-by-step interactive fix session."""
    issue = enrich_query(request.problem, request.device_model)
    actions = ACTION_CATALOG.get(issue["category"], ACTION_CATALOG["general"])

    session_id = str(uuid.uuid4())[:8]

    sessions[session_id] = {
        "session_id": session_id,
        "problem": request.problem,
        "issue": issue,
        "actions": actions,
        "current_step": 0,
        "step_history": [],
        "created_at": time.time(),
        "completed": False
    }

    current_action = actions[0]

    return {
        "session_id": session_id,
        "problem": request.problem,
        "issue": issue,
        "progress": {
            "current": 1,
            "total": len(actions),
            "percent": int((1 / len(actions)) * 100)
        },
        "current_action": current_action,
        "all_actions": [{"step": a["step"], "title": a["title"], "type": a["type"]} for a in actions],
        "message": f"Step 1 of {len(actions)}: {current_action['title']}"
    }

@app.get("/troubleshoot/{session_id}")
def get_session(session_id: str):
    """Retrieve existing session state."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Troubleshooting session not found")
    
    session = sessions[session_id]
    current_idx = session["current_step"]
    actions = session["actions"]

    is_completed = session["completed"] or current_idx >= len(actions)
    current_action = actions[current_idx] if not is_completed else None

    return {
        "session_id": session_id,
        "problem": session["problem"],
        "issue": session["issue"],
        "status": "completed" if is_completed else "in_progress",
        "progress": {
            "current": min(current_idx + 1, len(actions)),
            "total": len(actions),
            "percent": int((min(current_idx + 1, len(actions)) / len(actions)) * 100)
        },
        "current_action": current_action,
        "step_history": session.get("step_history", [])
    }

@app.post("/troubleshoot/{session_id}/complete")
def complete_step_legacy(session_id: str):
    """Compatibility route: advances session by one step."""
    return process_step_action(session_id, action="next")

@app.post("/troubleshoot/{session_id}/step")
def update_step(session_id: str, body: StepAction):
    """Rich step update route: supports 'next', 'prev', 'skip' with optional feedback."""
    return process_step_action(session_id, action=body.action, feedback=body.feedback)

def process_step_action(session_id: str, action: str = "next", feedback: Optional[str] = None):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Troubleshooting session not found")

    session = sessions[session_id]
    current_idx = session["current_step"]
    actions = session["actions"]

    # Record history
    if current_idx < len(actions):
        session.setdefault("step_history", []).append({
            "step": actions[current_idx]["step"],
            "title": actions[current_idx]["title"],
            "action_taken": action,
            "feedback": feedback,
            "timestamp": time.time()
        })

    if action == "prev":
        session["current_step"] = max(0, current_idx - 1)
        session["completed"] = False
    else:  # next or skip
        session["current_step"] = current_idx + 1

    # Check if finished
    if session["current_step"] >= len(actions):
        session["completed"] = True
        return {
            "session_id": session_id,
            "status": "completed",
            "message": "All recommended troubleshooting steps have been executed.",
            "verification": {
                "question": "Is your device working normally now?",
                "options": [
                    "Yes, the issue is completely fixed!",
                    "Partially resolved, but needs attention",
                    "No, the problem persists"
                ]
            },
            "history": session.get("step_history", [])
        }

    next_idx = session["current_step"]
    next_action = actions[next_idx]

    return {
        "session_id": session_id,
        "status": "in_progress",
        "progress": {
            "current": next_idx + 1,
            "total": len(actions),
            "percent": int(((next_idx + 1) / len(actions)) * 100)
        },
        "current_action": next_action,
        "message": f"Step {next_idx + 1} of {len(actions)}: {next_action['title']}"
    }

@app.post("/troubleshoot/{session_id}/reset")
def reset_session(session_id: str):
    """Reset session back to step 1."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Troubleshooting session not found")
    
    session = sessions[session_id]
    session["current_step"] = 0
    session["completed"] = False
    session["step_history"] = []

    return {
        "session_id": session_id,
        "status": "reset",
        "progress": {
            "current": 1,
            "total": len(session["actions"]),
            "percent": int((1 / len(session["actions"])) * 100)
        },
        "current_action": session["actions"][0]
    }
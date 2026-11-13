#!/usr/bin/env python3
"""OpenMontage Stage A - shared environment snapshot + P2.2 FFmpeg/NVENC.

Scope of this kernel (RUN_STAGE A): environment snapshot only, plus the
P2.2 FFmpeg software (libx264) and hardware (h264_nvenc) encode test.
No model weights are downloaded and no model inference is run here.

The shared helper below is embedded as base64 and verified by SHA256.
"""

import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

HELPER_B64 = "IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwoiIiJTaGFyZWQgS2FnZ2xlIGVudmlyb25tZW50IHNuYXBzaG90IGhlbHBlciBmb3IgdGhlIE9wZW5Nb250YWdlIGF1ZGl0LgoKVGhpcyBleGFjdCBmaWxlIG11c3QgYmUgY29waWVkIHVuY2hhbmdlZCBpbnRvIGV2ZXJ5IEthZ2dsZSBub3RlYm9vayBvZiB0aGUKYXVkaXQgKFN0YWdlIEEuLkQpLiBJdCByZWNvcmRzOgoKICAqIFVUQyB0aW1lc3RhbXAsIFB5dGhvbiB2ZXJzaW9uL2V4ZWN1dGFibGUsIHBpcCBmcmVlemUKICAqIHRvcmNoIHZlcnNpb24gLyBDVURBIGJ1aWxkIC8gYXZhaWxhYmlsaXR5IC8gZGV2aWNlIGNvdW50CiAgKiBwZXItZGV2aWNlIGluZGV4LCBuYW1lLCB0b3RhbCBtZW1vcnksIGNvbXB1dGUgY2FwYWJpbGl0eSwgZnJlZSBtZW1vcnkKICAqIGZ1bGwgbnZpZGlhLXNtaSBvdXRwdXQKICAqIEdQVSBuYW1lIC8gbWVtb3J5IC8gZHJpdmVyIC8gdXRpbGlzYXRpb24gLyBwcm9jZXNzIG1lbW9yeQogICogZmZtcGVnIC12ZXJzaW9uLCBmZm1wZWcgLWhpZGVfYmFubmVyIC1lbmNvZGVycywgZmZwcm9iZSAtdmVyc2lvbgogICogZGYgLWggL2thZ2dsZS93b3JraW5nLCAva2FnZ2xlL3RlbXAgKHdoZW4gcHJlc2VudCksIGZyZWUgLWgKICAqIENQVSBjb3VudAogICogc2hvcnQtdGltZW91dCBuZXR3b3JrIGNoZWNrIHRvIG9mZmljaWFsIHBhY2thZ2UvbW9kZWwgaG9zdHMKICAqIGZyZWUgc3BhY2UgYW5kIG91dHB1dC1kaXJlY3Rvcnkgc2l6ZQoKUmF3IGNvbW1hbmQgb3V0cHV0IGlzIHByZXNlcnZlZDsgbm8gY29tbWFuZCBmYWlsdXJlIGlzIHNpbGVudGx5IG9taXR0ZWQuCiIiIgoKZnJvbSBfX2Z1dHVyZV9fIGltcG9ydCBhbm5vdGF0aW9ucwoKaW1wb3J0IGpzb24KaW1wb3J0IG9zCmltcG9ydCBwbGF0Zm9ybQppbXBvcnQgc2h1dGlsCmltcG9ydCBzb2NrZXQKaW1wb3J0IHN1YnByb2Nlc3MKaW1wb3J0IHN5cwppbXBvcnQgdGltZQpmcm9tIGRhdGV0aW1lIGltcG9ydCBkYXRldGltZSwgdGltZXpvbmUKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCgpTTkFQU0hPVF9WRVJTSU9OID0gIjEuMC4wIgoKCmRlZiBfdXRjX25vdygpIC0+IHN0cjoKICAgIHJldHVybiBkYXRldGltZS5ub3codGltZXpvbmUudXRjKS5zdHJmdGltZSgiJVktJW0tJWRUJUg6JU06JVNaIikKCgpkZWYgcnVuX2NtZChjbWQsIHRpbWVvdXQ6IGludCA9IDEyMCk6CiAgICAiIiJSdW4gYSBjb21tYW5kIGFuZCByZXR1cm4gYSBzdHJ1Y3R1cmVkIHJlY29yZC4gTmV2ZXIgcmFpc2VzLiIiIgogICAgc3RhcnRlZCA9IHRpbWUudGltZSgpCiAgICByZWNvcmQgPSB7CiAgICAgICAgImNtZCI6IGNtZCBpZiBpc2luc3RhbmNlKGNtZCwgc3RyKSBlbHNlICIgIi5qb2luKGNtZCksCiAgICAgICAgInJldHVybmNvZGUiOiBOb25lLAogICAgICAgICJkdXJhdGlvbl9zIjogTm9uZSwKICAgICAgICAic3Rkb3V0IjogIiIsCiAgICAgICAgInN0ZGVyciI6ICIiLAogICAgfQogICAgdHJ5OgogICAgICAgIHByb2MgPSBzdWJwcm9jZXNzLnJ1bigKICAgICAgICAgICAgY21kLAogICAgICAgICAgICBzaGVsbD1pc2luc3RhbmNlKGNtZCwgc3RyKSwKICAgICAgICAgICAgY2FwdHVyZV9vdXRwdXQ9VHJ1ZSwKICAgICAgICAgICAgdGV4dD1UcnVlLAogICAgICAgICAgICB0aW1lb3V0PXRpbWVvdXQsCiAgICAgICAgKQogICAgICAgIHJlY29yZFsicmV0dXJuY29kZSJdID0gcHJvYy5yZXR1cm5jb2RlCiAgICAgICAgcmVjb3JkWyJzdGRvdXQiXSA9IHByb2Muc3Rkb3V0Wy00MDAwMDpdCiAgICAgICAgcmVjb3JkWyJzdGRlcnIiXSA9IHByb2Muc3RkZXJyWy0xNjAwMDpdCiAgICBleGNlcHQgRmlsZU5vdEZvdW5kRXJyb3IgYXMgZXhjOgogICAgICAgIHJlY29yZFsiZXJyb3IiXSA9IGYiRmlsZU5vdEZvdW5kRXJyb3I6IHtleGN9IgogICAgZXhjZXB0IHN1YnByb2Nlc3MuVGltZW91dEV4cGlyZWQ6CiAgICAgICAgcmVjb3JkWyJlcnJvciJdID0gZiJUaW1lb3V0RXhwaXJlZCBhZnRlciB7dGltZW91dH1zIgogICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBleGM6ICAjIG5vcWE6IEJMRTAwMSAtIGF1ZGl0IGhlbHBlciBtdXN0IG5ldmVyIGNyYXNoIHRoZSBydW4KICAgICAgICByZWNvcmRbImVycm9yIl0gPSBmInt0eXBlKGV4YykuX19uYW1lX199OiB7ZXhjfSIKICAgIHJlY29yZFsiZHVyYXRpb25fcyJdID0gcm91bmQodGltZS50aW1lKCkgLSBzdGFydGVkLCAzKQogICAgcmV0dXJuIHJlY29yZAoKCmRlZiBfdGFpbCh0ZXh0OiBzdHIsIGxpbWl0OiBpbnQgPSA0MDAwMCkgLT4gc3RyOgogICAgcmV0dXJuIHRleHRbLWxpbWl0Ol0gaWYgaXNpbnN0YW5jZSh0ZXh0LCBzdHIpIGVsc2UgIiIKCgpkZWYgX3BpcF9mcmVlemUoKSAtPiBzdHI6CiAgICB0cnk6CiAgICAgICAgcHJvYyA9IHN1YnByb2Nlc3MucnVuKAogICAgICAgICAgICBbc3lzLmV4ZWN1dGFibGUsICItbSIsICJwaXAiLCAiZnJlZXplIl0sCiAgICAgICAgICAgIGNhcHR1cmVfb3V0cHV0PVRydWUsCiAgICAgICAgICAgIHRleHQ9VHJ1ZSwKICAgICAgICAgICAgdGltZW91dD0xODAsCiAgICAgICAgKQogICAgICAgIHJldHVybiBwcm9jLnN0ZG91dAogICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBleGM6ICAjIG5vcWE6IEJMRTAwMQogICAgICAgIHJldHVybiBmInBpcCBmcmVlemUgZmFpbGVkOiB7dHlwZShleGMpLl9fbmFtZV9ffToge2V4Y30iCgoKZGVmIF90b3JjaF9pbmZvKCkgLT4gZGljdDoKICAgIGluZm8gPSB7CiAgICAgICAgInRvcmNoX2ltcG9ydGVkIjogRmFsc2UsCiAgICAgICAgInRvcmNoX3ZlcnNpb24iOiBOb25lLAogICAgICAgICJ0b3JjaF9jdWRhX2J1aWxkIjogTm9uZSwKICAgICAgICAiY3VkYV9hdmFpbGFibGUiOiBOb25lLAogICAgICAgICJkZXZpY2VfY291bnQiOiBOb25lLAogICAgICAgICJkZXZpY2VzIjogW10sCiAgICAgICAgImVycm9ycyI6IFtdLAogICAgfQogICAgdHJ5OgogICAgICAgIGltcG9ydCB0b3JjaCAgIyBub3FhOiBQTEMwNDE1CiAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGV4YzogICMgbm9xYTogQkxFMDAxCiAgICAgICAgaW5mb1siZXJyb3JzIl0uYXBwZW5kKGYiaW1wb3J0IHRvcmNoIGZhaWxlZDoge3R5cGUoZXhjKS5fX25hbWVfX306IHtleGN9IikKICAgICAgICByZXR1cm4gaW5mbwoKICAgIGluZm9bInRvcmNoX2ltcG9ydGVkIl0gPSBUcnVlCiAgICBpbmZvWyJ0b3JjaF92ZXJzaW9uIl0gPSBnZXRhdHRyKHRvcmNoLCAiX192ZXJzaW9uX18iLCBOb25lKQogICAgaW5mb1sidG9yY2hfY3VkYV9idWlsZCJdID0gZ2V0YXR0cihnZXRhdHRyKHRvcmNoLCAidmVyc2lvbiIsIE5vbmUpLCAiY3VkYSIsIE5vbmUpCiAgICB0cnk6CiAgICAgICAgaW5mb1siY3VkYV9hdmFpbGFibGUiXSA9IGJvb2wodG9yY2guY3VkYS5pc19hdmFpbGFibGUoKSkKICAgICAgICBpbmZvWyJkZXZpY2VfY291bnQiXSA9IGludCh0b3JjaC5jdWRhLmRldmljZV9jb3VudCgpKQogICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBleGM6ICAjIG5vcWE6IEJMRTAwMQogICAgICAgIGluZm9bImVycm9ycyJdLmFwcGVuZChmImN1ZGEgcXVlcnkgZmFpbGVkOiB7dHlwZShleGMpLl9fbmFtZV9ffToge2V4Y30iKQogICAgICAgIHJldHVybiBpbmZvCgogICAgZm9yIGlkeCBpbiByYW5nZShpbmZvWyJkZXZpY2VfY291bnQiXSBvciAwKToKICAgICAgICBkZXZpY2UgPSB7ImluZGV4IjogaWR4fQogICAgICAgIHRyeToKICAgICAgICAgICAgcHJvcHMgPSB0b3JjaC5jdWRhLmdldF9kZXZpY2VfcHJvcGVydGllcyhpZHgpCiAgICAgICAgICAgIGRldmljZS51cGRhdGUoCiAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgIm5hbWUiOiBwcm9wcy5uYW1lLAogICAgICAgICAgICAgICAgICAgICJ0b3RhbF9tZW1vcnlfbWliIjogaW50KHByb3BzLnRvdGFsX21lbW9yeSAvICgxMDI0ICogMTAyNCkpLAogICAgICAgICAgICAgICAgICAgICJjb21wdXRlX2NhcGFiaWxpdHkiOiBmIntwcm9wcy5tYWpvcn0ue3Byb3BzLm1pbm9yfSIsCiAgICAgICAgICAgICAgICAgICAgIm11bHRpX3Byb2Nlc3Nvcl9jb3VudCI6IGdldGF0dHIocHJvcHMsICJtdWx0aV9wcm9jZXNzb3JfY291bnQiLCBOb25lKSwKICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgKQogICAgICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZXhjOiAgIyBub3FhOiBCTEUwMDEKICAgICAgICAgICAgZGV2aWNlWyJlcnJvciJdID0gZiJ7dHlwZShleGMpLl9fbmFtZV9ffToge2V4Y30iCiAgICAgICAgdHJ5OgogICAgICAgICAgICBmcmVlX2J5dGVzLCB0b3RhbF9ieXRlcyA9IHRvcmNoLmN1ZGEubWVtX2dldF9pbmZvKGlkeCkKICAgICAgICAgICAgZGV2aWNlWyJmcmVlX21lbW9yeV9taWIiXSA9IGludChmcmVlX2J5dGVzIC8gKDEwMjQgKiAxMDI0KSkKICAgICAgICAgICAgZGV2aWNlWyJ0b3RhbF9tZW1vcnlfbWliX3JlcG9ydGVkIl0gPSBpbnQodG90YWxfYnl0ZXMgLyAoMTAyNCAqIDEwMjQpKQogICAgICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZXhjOiAgIyBub3FhOiBCTEUwMDEKICAgICAgICAgICAgZGV2aWNlWyJtZW1fZ2V0X2luZm9fZXJyb3IiXSA9IGYie3R5cGUoZXhjKS5fX25hbWVfX306IHtleGN9IgogICAgICAgIGluZm9bImRldmljZXMiXS5hcHBlbmQoZGV2aWNlKQogICAgcmV0dXJuIGluZm8KCgpkZWYgX252aWRpYV9zbWkoKSAtPiBkaWN0OgogICAgcmV0dXJuIHJ1bl9jbWQoWyJudmlkaWEtc21pIl0sIHRpbWVvdXQ9NjApCgoKZGVmIF9uZXR3b3JrX2NoZWNrKGhvc3RzPU5vbmUsIHRpbWVvdXQ6IGZsb2F0ID0gNS4wKSAtPiBsaXN0OgogICAgaG9zdHMgPSBob3N0cyBvciBbImh1Z2dpbmdmYWNlLmNvIiwgInB5cGkub3JnIiwgImdpdGh1Yi5jb20iXQogICAgcmVzdWx0cyA9IFtdCiAgICBmb3IgaG9zdCBpbiBob3N0czoKICAgICAgICBpdGVtID0geyJob3N0IjogaG9zdCwgInBvcnQiOiA0NDN9CiAgICAgICAgc3RhcnRlZCA9IHRpbWUudGltZSgpCiAgICAgICAgdHJ5OgogICAgICAgICAgICB3aXRoIHNvY2tldC5jcmVhdGVfY29ubmVjdGlvbigoaG9zdCwgNDQzKSwgdGltZW91dD10aW1lb3V0KToKICAgICAgICAgICAgICAgIGl0ZW1bInJlYWNoYWJsZSJdID0gVHJ1ZQogICAgICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZXhjOiAgIyBub3FhOiBCTEUwMDEKICAgICAgICAgICAgaXRlbVsicmVhY2hhYmxlIl0gPSBGYWxzZQogICAgICAgICAgICBpdGVtWyJlcnJvciJdID0gZiJ7dHlwZShleGMpLl9fbmFtZV9ffToge2V4Y30iCiAgICAgICAgaXRlbVsibGF0ZW5jeV9zIl0gPSByb3VuZCh0aW1lLnRpbWUoKSAtIHN0YXJ0ZWQsIDMpCiAgICAgICAgcmVzdWx0cy5hcHBlbmQoaXRlbSkKICAgIHJldHVybiByZXN1bHRzCgoKZGVmIF9kaXJfc2l6ZShwYXRoOiBQYXRoKSAtPiBkaWN0OgogICAgcGF0aCA9IFBhdGgocGF0aCkKICAgIGlmIG5vdCBwYXRoLmV4aXN0cygpOgogICAgICAgIHJldHVybiB7InBhdGgiOiBzdHIocGF0aCksICJleGlzdHMiOiBGYWxzZSwgImJ5dGVzIjogTm9uZX0KICAgIHRvdGFsID0gMAogICAgZmlsZXMgPSAwCiAgICB0cnk6CiAgICAgICAgZm9yIHJvb3QsIF9kaXJzLCBuYW1lcyBpbiBvcy53YWxrKHBhdGgpOgogICAgICAgICAgICBmb3IgbmFtZSBpbiBuYW1lczoKICAgICAgICAgICAgICAgIHRyeToKICAgICAgICAgICAgICAgICAgICB0b3RhbCArPSBvcy5wYXRoLmdldHNpemUob3MucGF0aC5qb2luKHJvb3QsIG5hbWUpKQogICAgICAgICAgICAgICAgICAgIGZpbGVzICs9IDEKICAgICAgICAgICAgICAgIGV4Y2VwdCBPU0Vycm9yOgogICAgICAgICAgICAgICAgICAgIGNvbnRpbnVlCiAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGV4YzogICMgbm9xYTogQkxFMDAxCiAgICAgICAgcmV0dXJuIHsicGF0aCI6IHN0cihwYXRoKSwgImV4aXN0cyI6IFRydWUsICJlcnJvciI6IGYie3R5cGUoZXhjKS5fX25hbWVfX306IHtleGN9In0KICAgIHJldHVybiB7InBhdGgiOiBzdHIocGF0aCksICJleGlzdHMiOiBUcnVlLCAiYnl0ZXMiOiB0b3RhbCwgImZpbGVzIjogZmlsZXN9CgoKZGVmIGNvbGxlY3Qob3V0X2Rpcjogc3RyIHwgb3MuUGF0aExpa2UsIGxhYmVsOiBzdHIpIC0+IGRpY3Q6CiAgICAiIiJDb2xsZWN0IGEgZnVsbCBzbmFwc2hvdCBhbmQgcGVyc2lzdCBKU09OICsgcmF3IHRleHQuIFJldHVybnMgdGhlIGRpY3QuIiIiCiAgICBvdXRfcGF0aCA9IFBhdGgob3V0X2RpcikKICAgIG91dF9wYXRoLm1rZGlyKHBhcmVudHM9VHJ1ZSwgZXhpc3Rfb2s9VHJ1ZSkKICAgIHN0YW1wID0gX3V0Y19ub3coKQoKICAgIHBheWxvYWQgPSB7CiAgICAgICAgInNuYXBzaG90X3ZlcnNpb24iOiBTTkFQU0hPVF9WRVJTSU9OLAogICAgICAgICJsYWJlbCI6IGxhYmVsLAogICAgICAgICJ1dGNfdGltZXN0YW1wIjogc3RhbXAsCiAgICAgICAgImhvc3RuYW1lIjogc29ja2V0LmdldGhvc3RuYW1lKCksCiAgICAgICAgInBsYXRmb3JtIjogcGxhdGZvcm0ucGxhdGZvcm0oKSwKICAgICAgICAicHl0aG9uX3ZlcnNpb24iOiBzeXMudmVyc2lvbiwKICAgICAgICAicHl0aG9uX2V4ZWN1dGFibGUiOiBzeXMuZXhlY3V0YWJsZSwKICAgICAgICAicGlwX2ZyZWV6ZSI6IF9waXBfZnJlZXplKCksCiAgICAgICAgInRvcmNoIjogX3RvcmNoX2luZm8oKSwKICAgICAgICAibnZpZGlhX3NtaSI6IF9udmlkaWFfc21pKCksCiAgICAgICAgImZmbXBlZ192ZXJzaW9uIjogcnVuX2NtZChbImZmbXBlZyIsICItdmVyc2lvbiJdLCB0aW1lb3V0PTYwKSwKICAgICAgICAiZmZtcGVnX2VuY29kZXJzIjogcnVuX2NtZChbImZmbXBlZyIsICItaGlkZV9iYW5uZXIiLCAiLWVuY29kZXJzIl0sIHRpbWVvdXQ9MTIwKSwKICAgICAgICAiZmZwcm9iZV92ZXJzaW9uIjogcnVuX2NtZChbImZmcHJvYmUiLCAiLXZlcnNpb24iXSwgdGltZW91dD02MCksCiAgICAgICAgImRmX3dvcmtpbmciOiBydW5fY21kKFsiZGYiLCAiLWgiLCAiL2thZ2dsZS93b3JraW5nIl0sIHRpbWVvdXQ9MzApLAogICAgICAgICJkZl90ZW1wIjogcnVuX2NtZChbImRmIiwgIi1oIiwgIi9rYWdnbGUvdGVtcCJdLCB0aW1lb3V0PTMwKSwKICAgICAgICAiZnJlZV9oIjogcnVuX2NtZChbImZyZWUiLCAiLWgiXSwgdGltZW91dD0zMCksCiAgICAgICAgImNwdV9jb3VudCI6IG9zLmNwdV9jb3VudCgpLAogICAgICAgICJuZXR3b3JrX2NoZWNrIjogX25ldHdvcmtfY2hlY2soKSwKICAgICAgICAib3V0cHV0X2Rpcl9zaXplIjogX2Rpcl9zaXplKG91dF9wYXRoKSwKICAgICAgICAiZGlza191c2FnZSI6IHsKICAgICAgICAgICAgIndvcmtpbmdfZnJlZV9naWIiOiBzaHV0aWwuZGlza191c2FnZSgiL2thZ2dsZS93b3JraW5nIikuZnJlZSAvICgxMDI0KiozKQogICAgICAgICAgICBpZiBQYXRoKCIva2FnZ2xlL3dvcmtpbmciKS5leGlzdHMoKQogICAgICAgICAgICBlbHNlIE5vbmUKICAgICAgICB9LAogICAgfQoKICAgIGpzb25fcGF0aCA9IG91dF9wYXRoIC8gZiJlbnZpcm9ubWVudF9zbmFwc2hvdF97bGFiZWx9Lmpzb24iCiAgICBqc29uX3BhdGgud3JpdGVfdGV4dChqc29uLmR1bXBzKHBheWxvYWQsIGluZGVudD0yLCBzb3J0X2tleXM9VHJ1ZSksIGVuY29kaW5nPSJ1dGYtOCIpCgogICAgcmF3X2xpbmVzID0gW2YiPT09PT0gU05BUFNIT1Qge2xhYmVsfSBAIHtzdGFtcH0gPT09PT0iXQogICAgZm9yIGtleSBpbiAoCiAgICAgICAgInB5dGhvbl92ZXJzaW9uIiwKICAgICAgICAicGxhdGZvcm0iLAogICAgICAgICJjcHVfY291bnQiLAogICAgICAgICJudmlkaWFfc21pIiwKICAgICAgICAiZmZtcGVnX3ZlcnNpb24iLAogICAgICAgICJmZnByb2JlX3ZlcnNpb24iLAogICAgICAgICJkZl93b3JraW5nIiwKICAgICAgICAiZGZfdGVtcCIsCiAgICAgICAgImZyZWVfaCIsCiAgICAgICAgIm5ldHdvcmtfY2hlY2siLAogICAgKToKICAgICAgICByYXdfbGluZXMuYXBwZW5kKGYiLS0tIHtrZXl9IC0tLSIpCiAgICAgICAgdmFsdWUgPSBwYXlsb2FkLmdldChrZXkpCiAgICAgICAgaWYgaXNpbnN0YW5jZSh2YWx1ZSwgZGljdCk6CiAgICAgICAgICAgIHJhd19saW5lcy5hcHBlbmQoZiJyZXR1cm5jb2RlPXt2YWx1ZS5nZXQoJ3JldHVybmNvZGUnKX0iKQogICAgICAgICAgICByYXdfbGluZXMuYXBwZW5kKHZhbHVlLmdldCgic3Rkb3V0IiwgIiIpKQogICAgICAgICAgICBpZiB2YWx1ZS5nZXQoInN0ZGVyciIpOgogICAgICAgICAgICAgICAgcmF3X2xpbmVzLmFwcGVuZCgiW3N0ZGVycl0gIiArIHZhbHVlWyJzdGRlcnIiXSkKICAgICAgICAgICAgaWYgdmFsdWUuZ2V0KCJlcnJvciIpOgogICAgICAgICAgICAgICAgcmF3X2xpbmVzLmFwcGVuZCgiW2Vycm9yXSAiICsgc3RyKHZhbHVlWyJlcnJvciJdKSkKICAgICAgICBlbHNlOgogICAgICAgICAgICByYXdfbGluZXMuYXBwZW5kKGpzb24uZHVtcHModmFsdWUsIGluZGVudD0yLCBzb3J0X2tleXM9VHJ1ZSkpCiAgICByYXdfbGluZXMuYXBwZW5kKCItLS0gdG9yY2ggLS0tIikKICAgIHJhd19saW5lcy5hcHBlbmQoanNvbi5kdW1wcyhwYXlsb2FkWyJ0b3JjaCJdLCBpbmRlbnQ9Miwgc29ydF9rZXlzPVRydWUpKQogICAgcmF3X2xpbmVzLmFwcGVuZCgiLS0tIHBpcCBmcmVlemUgLS0tIikKICAgIHJhd19saW5lcy5hcHBlbmQocGF5bG9hZFsicGlwX2ZyZWV6ZSJdKQogICAgcmF3X3BhdGggPSBvdXRfcGF0aCAvIGYiZW52aXJvbm1lbnRfc25hcHNob3Rfe2xhYmVsfS50eHQiCiAgICByYXdfcGF0aC53cml0ZV90ZXh0KCJcbiIuam9pbihyYXdfbGluZXMpLCBlbmNvZGluZz0idXRmLTgiKQoKICAgIHJldHVybiBwYXlsb2FkCgoKZGVmIGFzc2VydF90NChwYXlsb2FkOiBkaWN0KSAtPiBkaWN0OgogICAgIiIiUmV0dXJuIGEgVDQgdmVyaWZpY2F0aW9uIHJlY29yZC4gTmV2ZXIgcmFpc2VzOyBjYWxsZXIgZGVjaWRlcyB0byBzdG9wLiIiIgogICAgdG9yY2hfaW5mbyA9IHBheWxvYWQuZ2V0KCJ0b3JjaCIsIHt9KQogICAgZGV2aWNlcyA9IHRvcmNoX2luZm8uZ2V0KCJkZXZpY2VzIiwgW10pCiAgICByZWNvcmQgPSB7CiAgICAgICAgImN1ZGFfYXZhaWxhYmxlIjogdG9yY2hfaW5mby5nZXQoImN1ZGFfYXZhaWxhYmxlIiksCiAgICAgICAgImRldmljZV9jb3VudCI6IHRvcmNoX2luZm8uZ2V0KCJkZXZpY2VfY291bnQiKSwKICAgICAgICAiYWxsX2RldmljZXNfYXJlX3Rlc2xhX3Q0IjogRmFsc2UsCiAgICAgICAgInBlcl9kZXZpY2UiOiBbXSwKICAgICAgICAib2siOiBGYWxzZSwKICAgICAgICAicmVhc29ucyI6IFtdLAogICAgfQogICAgaWYgbm90IHRvcmNoX2luZm8uZ2V0KCJjdWRhX2F2YWlsYWJsZSIpOgogICAgICAgIHJlY29yZFsicmVhc29ucyJdLmFwcGVuZCgidG9yY2guY3VkYS5pc19hdmFpbGFibGUoKSBpcyBmYWxzZSIpCiAgICBpZiBub3QgdG9yY2hfaW5mby5nZXQoImRldmljZV9jb3VudCIpIGluICgxLCAyKToKICAgICAgICByZWNvcmRbInJlYXNvbnMiXS5hcHBlbmQoCiAgICAgICAgICAgIGYiZGV2aWNlX2NvdW50PXt0b3JjaF9pbmZvLmdldCgnZGV2aWNlX2NvdW50Jykhcn0gaXMgbm90IDEgb3IgMiIKICAgICAgICApCiAgICBmb3IgZGV2aWNlIGluIGRldmljZXM6CiAgICAgICAgaXRlbSA9IHsKICAgICAgICAgICAgImluZGV4IjogZGV2aWNlLmdldCgiaW5kZXgiKSwKICAgICAgICAgICAgIm5hbWUiOiBkZXZpY2UuZ2V0KCJuYW1lIiksCiAgICAgICAgICAgICJ0b3RhbF9tZW1vcnlfbWliIjogZGV2aWNlLmdldCgidG90YWxfbWVtb3J5X21pYiIpLAogICAgICAgICAgICAiY29tcHV0ZV9jYXBhYmlsaXR5IjogZGV2aWNlLmdldCgiY29tcHV0ZV9jYXBhYmlsaXR5IiksCiAgICAgICAgICAgICJmcmVlX21lbW9yeV9taWIiOiBkZXZpY2UuZ2V0KCJmcmVlX21lbW9yeV9taWIiKSwKICAgICAgICB9CiAgICAgICAgbmFtZSA9IChkZXZpY2UuZ2V0KCJuYW1lIikgb3IgIiIpLnVwcGVyKCkKICAgICAgICBpZiAiVEVTTEEgVDQiIG5vdCBpbiBuYW1lOgogICAgICAgICAgICByZWNvcmRbInJlYXNvbnMiXS5hcHBlbmQoZiJkZXZpY2Uge2RldmljZS5nZXQoJ2luZGV4Jyl9IGlzIG5vdCBhIFRlc2xhIFQ0OiB7ZGV2aWNlLmdldCgnbmFtZScpIXJ9IikKICAgICAgICBpZiBkZXZpY2UuZ2V0KCJjb21wdXRlX2NhcGFiaWxpdHkiKSBub3QgaW4gKCI3LjUiLCBOb25lKToKICAgICAgICAgICAgcmVjb3JkWyJyZWFzb25zIl0uYXBwZW5kKAogICAgICAgICAgICAgICAgZiJkZXZpY2Uge2RldmljZS5nZXQoJ2luZGV4Jyl9IGNvbXB1dGUgY2FwYWJpbGl0eSB7ZGV2aWNlLmdldCgnY29tcHV0ZV9jYXBhYmlsaXR5Jyl9ICE9IDcuNSIKICAgICAgICAgICAgKQogICAgICAgIHJlY29yZFsicGVyX2RldmljZSJdLmFwcGVuZChpdGVtKQogICAgcmVjb3JkWyJhbGxfZGV2aWNlc19hcmVfdGVzbGFfdDQiXSA9IGFsbCgKICAgICAgICAiVEVTTEEgVDQiIGluIChkLmdldCgibmFtZSIpIG9yICIiKS51cHBlcigpIGZvciBkIGluIGRldmljZXMKICAgICkgYW5kIGJvb2woZGV2aWNlcykKICAgIHJlY29yZFsib2siXSA9IHJlY29yZFsiYWxsX2RldmljZXNfYXJlX3Rlc2xhX3Q0Il0gYW5kIG5vdCByZWNvcmRbInJlYXNvbnMiXQogICAgcmV0dXJuIHJlY29yZAoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBpbXBvcnQgYXJncGFyc2UKCiAgICBwYXJzZXIgPSBhcmdwYXJzZS5Bcmd1bWVudFBhcnNlcihkZXNjcmlwdGlvbj0iS2FnZ2xlIGVudmlyb25tZW50IHNuYXBzaG90IikKICAgIHBhcnNlci5hZGRfYXJndW1lbnQoIi0tb3V0IiwgZGVmYXVsdD0iL2thZ2dsZS93b3JraW5nL2F1ZGl0L2xvZ3Mva2FnZ2xlIikKICAgIHBhcnNlci5hZGRfYXJndW1lbnQoIi0tbGFiZWwiLCBkZWZhdWx0PSJtYW51YWwiKQogICAgYXJncyA9IHBhcnNlci5wYXJzZV9hcmdzKCkKICAgIHJlc3VsdCA9IGNvbGxlY3QoYXJncy5vdXQsIGFyZ3MubGFiZWwpCiAgICBwcmludChqc29uLmR1bXBzKHsibGFiZWwiOiBhcmdzLmxhYmVsLCAidG9yY2giOiByZXN1bHRbInRvcmNoIl0sICJ0NCI6IGFzc2VydF90NChyZXN1bHQpfSwgaW5kZW50PTIpKQ=="
HELPER_SHA256 = "1edc961ebd671ba9f628cc78f136e56ebdcbb83d3943a7d012c16e663253d56a"

WORK = Path("/kaggle/working/audit")
LOGS = WORK / "logs/kaggle"
RESULTS = WORK / "results"
PREVIEWS = WORK / "previews"
for _p in (WORK, LOGS, RESULTS, PREVIEWS, WORK / "scripts"):
    _p.mkdir(parents=True, exist_ok=True)


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sh(cmd, timeout=900):
    started = time.time()
    rec = {"cmd": cmd, "returncode": None, "duration_s": None, "stdout": "", "stderr": ""}
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        rec["returncode"] = proc.returncode
        rec["stdout"] = proc.stdout[-40000:]
        rec["stderr"] = proc.stderr[-16000:]
    except Exception as exc:  # noqa: BLE001
        rec["error"] = f"{type(exc).__name__}: {exc}"
    rec["duration_s"] = round(time.time() - started, 3)
    return rec


def main() -> int:
    run_started = time.time()
    report = {
        "stage": "A",
        "kernel_purpose": "shared environment snapshot + P2.2 FFmpeg/NVENC",
        "utc_start": utc(),
        "status": "UNKNOWN",
        "steps": {},
    }

    # --- 1. materialise and verify the shared helper -----------------------
    helper_path = WORK / "scripts/kaggle_environment_snapshot.py"
    helper_path.write_bytes(base64.b64decode(HELPER_B64))
    actual_helper_sha = sha256_file(helper_path)
    report["helper"] = {
        "path": str(helper_path),
        "embedded_sha256": HELPER_SHA256,
        "actual_sha256": actual_helper_sha,
        "match": actual_helper_sha == HELPER_SHA256,
    }
    print("helper sha256:", actual_helper_sha, "match:", actual_helper_sha == HELPER_SHA256)
    if actual_helper_sha != HELPER_SHA256:
        report["status"] = "BLOCKED"
        report["blocker"] = "shared helper SHA256 mismatch"
        (LOGS / "stage_a_summary.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return 1

    sys.path.insert(0, str(helper_path.parent))
    import kaggle_environment_snapshot as snap  # noqa: PLC0415

    # --- 2. environment snapshot BEFORE ------------------------------------
    before = snap.collect(LOGS, "before")
    t4 = snap.assert_t4(before)
    report["steps"]["environment_before"] = {
        "utc_timestamp": before["utc_timestamp"],
        "python_version": before["python_version"],
        "torch": {
            "version": before["torch"]["torch_version"],
            "cuda_build": before["torch"]["torch_cuda_build"],
            "cuda_available": before["torch"]["cuda_available"],
            "device_count": before["torch"]["device_count"],
            "devices": before["torch"]["devices"],
        },
        "ffmpeg_version_returncode": before["ffmpeg_version"]["returncode"],
        "ffmpeg_version_first_line": (before["ffmpeg_version"]["stdout"].splitlines() or [""])[0],
        "ffprobe_version_first_line": (before["ffprobe_version"]["stdout"].splitlines() or [""])[0],
        "network_check": before["network_check"],
        "t4_assertion": t4,
    }
    print("T4 assertion:", json.dumps(t4))
    if not t4["ok"]:
        report["status"] = "BLOCKED"
        report["blocker"] = "GPU assertion failed: " + "; ".join(t4["reasons"])
        (LOGS / "stage_a_summary.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return 2

    # --- 3. P2.2 FFmpeg build + NVENC --------------------------------------
    encoders = before["ffmpeg_encoders"]
    enc_text = (enc_text_val := encoders.get("stdout", "")) or ""
    has_libx264 = "libx264" in enc_text
    has_nvenc = "h264_nvenc" in enc_text
    nvenc_help = sh("ffmpeg -hide_banner -h encoder=h264_nvenc", timeout=60)
    report["steps"]["p2_2_ffmpeg_build"] = {
        "libx264_present": has_libx264,
        "h264_nvenc_present": has_nvenc,
        "nvenc_help_returncode": nvenc_help["returncode"],
        "nvenc_help_first_lines": "\n".join(nvenc_help["stdout"].splitlines()[:25]),
        "configuration": next(
            (line for line in enc_text.splitlines() if line.strip().startswith("configuration:")),
            None,
        ),
        "encoder_list_sha256": hashlib.sha256(enc_text.encode("utf-8", "replace")).hexdigest(),
    }

    # deterministic 10 s 1920x1080 30 fps testsrc2 + 48 kHz tone
    src = (
        "ffmpeg -y -hide_banner -loglevel error "
        "-f lavfi -i testsrc2=size=1920x1080:rate=30:duration=10 "
        "-f lavfi -i sine=frequency=440:sample_rate=48000:duration=10 "
        "-c:v libx264 -preset ultrafast -qp 0 -pix_fmt yuv420p "
        "-c:a pcm_s16le -shortest /kaggle/working/audit/previews/p2_2_source.mp4"
    )
    src_run = sh(src, timeout=600)
    report["steps"]["source_generation"] = {
        "cmd": src,
        "returncode": src_run["returncode"],
        "duration_s": src_run["duration_s"],
        "stderr": src_run["stderr"][-4000:],
    }

    def sample_gpu(path: Path, seconds: int = 8) -> subprocess.Popen:
        cmd = (
            f"timeout {seconds} nvidia-smi "
            "--query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader -l 1 "
            f"> {path} 2>&1"
        )
        return subprocess.Popen(cmd, shell=True)

    def encode_case(name: str, cmd: str) -> dict:
        out = f"/kaggle/working/audit/previews/p2_2_{name}.mp4"
        full = cmd.replace("<<OUT>>", out)
        sampler = None
        samples_path = LOGS / f"p2_2_{name}_nvidia_smi.csv"
        if name == "h264_nvenc":
            sampler = sample_gpu(samples_path, 8)
            time.sleep(0.5)
        run = sh(full, timeout=900)
        if sampler is not None:
            try:
                sampler.wait(timeout=12)
            except Exception:  # noqa: BLE001
                sampler.kill()
        rec = {
            "name": name,
            "cmd": full,
            "returncode": run["returncode"],
            "duration_s": run["duration_s"],
            "stderr": run["stderr"][-6000:],
            "output": None,
            "probe": None,
            "decode": None,
        }
        if samples_path.exists():
            lines = [l for l in samples_path.read_text(errors="replace").splitlines() if l.strip()]
            rec["nvidia_smi_samples"] = lines[:20]
            rec["nvidia_smi_sample_count"] = len(lines)
        if Path(out).exists() and Path(out).stat().st_size > 0:
            rec["output"] = {
                "path": out,
                "bytes": Path(out).stat().st_size,
                "sha256": sha256_file(Path(out)),
            }
            probe = sh(
                f"ffprobe -v error -show_streams -show_format -of json {out}", timeout=120
            )
            try:
                rec["probe"] = json.loads(probe["stdout"])
            except Exception:  # noqa: BLE001
                rec["probe"] = {"parse_error": True, "raw": probe["stdout"][-4000:]}
            decode = sh(f"ffmpeg -v error -i {out} -f null -", timeout=600)
            rec["decode"] = {
                "returncode": decode["returncode"],
                "stderr": decode["stderr"][-8000:],
                "clean": decode["returncode"] == 0 and not decode["stderr"].strip(),
            }
        return rec

    libx264 = None
    if has_libx264:
        libx264 = encode_case(
            "libx264",
            "ffmpeg -y -hide_banner -loglevel error "
            "-f lavfi -i testsrc2=size=1920x1080:rate=30:duration=10 "
            "-f lavfi -i sine=frequency=440:sample_rate=48000:duration=10 "
            "-c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p "
            "-c:a aac -b:a 128k -shortest <<OUT>>",
        )
        probe = libx264.get("probe") or {}
        streams = probe.get("streams", []) if isinstance(probe, dict) else []
        video = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
        libx264["checks"] = {
            "video_codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "avg_frame_rate": video.get("avg_frame_rate"),
            "nb_frames": video.get("nb_frames"),
            "pix_fmt": video.get("pix_fmt"),
            "audio_codec": audio.get("codec_name"),
            "sample_rate": audio.get("sample_rate"),
            "duration_s": float((probe.get("format") or {}).get("duration") or 0),
            "valid_10s_1080p30": (
                video.get("codec_name") == "h264"
                and video.get("width") == 1920
                and video.get("height") == 1080
                and video.get("avg_frame_rate") == "30/1"
                and abs(float((probe.get("format") or {}).get("duration") or 0) - 10.0) < 0.5
            ),
        }
        libx264["pass"] = bool(
            libx264["returncode"] == 0
            and libx264.get("decode", {}).get("clean")
            and libx264["checks"]["valid_10s_1080p30"]
        )

    nvenc = None
    if has_nvenc:
        nvenc = encode_case(
            "h264_nvenc",
            "ffmpeg -y -hide_banner -loglevel error "
            "-f lavfi -i testsrc2=size=1920x1080:rate=30:duration=10 "
            "-f lavfi -i sine=frequency=440:sample_rate=48000:duration=10 "
            "-c:v h264_nvenc -preset p4 -rc vbr -cq 23 -b:v 0 -pix_fmt yuv420p "
            "-c:a aac -b:a 128k -shortest <<OUT>>",
        )
        probe = nvenc.get("probe") or {}
        streams = probe.get("streams", []) if isinstance(probe, dict) else []
        video = next((s for s in streams if s.get("codec_type") == "video"), {})
        nvenc["checks"] = {
            "video_codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "avg_frame_rate": video.get("avg_frame_rate"),
            "nb_frames": video.get("nb_frames"),
            "duration_s": float((probe.get("format") or {}).get("duration") or 0),
        }
        nvenc["pass"] = bool(
            nvenc["returncode"] == 0
            and nvenc.get("decode", {}).get("clean")
            and video.get("codec_name") == "h264"
            and video.get("width") == 1920
            and video.get("height") == 1080
        )

    report["steps"]["p2_2_results"] = {
        "libx264": libx264,
        "h264_nvenc": nvenc,
        "nvenc_tested": has_nvenc,
        "note": "libx264 PASS does not imply NVENC PASS",
    }

    # --- 4. snapshot AFTER -------------------------------------------------
    after = snap.collect(LOGS, "after")
    report["steps"]["environment_after"] = {
        "utc_timestamp": after["utc_timestamp"],
        "torch": {
            "version": after["torch"]["torch_version"],
            "cuda_available": after["torch"]["cuda_available"],
            "device_count": after["torch"]["device_count"],
            "devices": after["torch"]["devices"],
        },
        "network_check": after["network_check"],
        "disk_usage": after["disk_usage"],
        "working_dir_size": after["output_dir_size"],
    }
    report["utc_end"] = utc()
    report["wall_seconds"] = round(time.time() - run_started, 3)

    libx264_ok = bool((libx264 or {}).get("pass"))
    nvenc_present = has_nvenc
    nvenc_ok = bool((nvenc or {}).get("pass"))
    if not has_libx264:
        report["status"] = "FAIL"
        report["blocker"] = "libx264 encoder missing"
    elif not libx264_ok:
        report["status"] = "FAIL"
        report["blocker"] = "libx264 encode/decode/validation failed"
    elif nvenc_present and not nvenc_ok:
        report["status"] = "FAIL"
        report["blocker"] = "h264_nvenc present but encode/decode/validation failed"
    elif not nvenc_present:
        report["status"] = "PASS"
        report["nvenc_status"] = "FAIL (encoder missing)"
    else:
        report["status"] = "PASS"
        report["nvenc_status"] = "PASS"
    report["libx264_status"] = "PASS" if libx264_ok else "FAIL"

    (LOGS / "stage_a_summary.json").write_text(json.dumps(report, indent=2))
    (LOGS / "stage_a_summary.txt").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        print(tb)
        try:
            (LOGS / "stage_a_summary.json").write_text(
                json.dumps(
                    {
                        "stage": "A",
                        "status": "FAIL",
                        "blocker": "unhandled exception",
                        "traceback": tb,
                        "utc_end": utc(),
                    },
                    indent=2,
                )
            )
        except Exception:  # noqa: BLE001
            pass
        raise SystemExit(4)

import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "deletion_requests.csv"), "r", encoding="utf-8") as f:
    all_requests = list(csv.DictReader(f))

# Let's inspect all unique patterns or categories of request_text
for r in all_requests:
    text = r["request_text"]
    # Look for access/export/rectify/marketing/opt-out keywords in any language
    # English, French, Spanish, Portuguese, German, Italian, Japanese, Korean, etc.
    t_lower = text.lower()
    # Check if text is non-deletion
    is_access = any(w in t_lower for w in ["access", "accès", "acceso", "zugang", "열람", "アクセス", "export", "download", "herunterladen", "télécharger", "descargar", "baixar", "내보내기", "ダウンロード", "copy of my personal data", "copia de mis datos", "copie de mes données", "kopie meiner", "meine daten einsehen"])
    is_correct = any(w in t_lower for w in ["correct", "rectif", "korrigieren", "corregir", "corrigir", "수정", "訂正", "update my phone", "update my email", "change my name"])
    is_optout = any(w in t_lower for w in ["opt-out", "opt out", "unsubscribe", "abmelden", "désabonner", "cancelar suscripción", "수신 거부", "配信停止", "marketing emails", "newsletter", "promotional messages"])
    
    # Check if text also contains deletion terms
    has_del = any(w in t_lower for w in ["delete", "delet", "eras", "remov", "close", "suppression", "supprimer", "eliminar", "eliminación", "exclusão", "excluir", "lösch", "löschung", "cancellazione", "cancella", "削除", "삭제", "destroy"])

    if (is_access or is_correct or is_optout) and not has_del:
        print(f"NON_DEL_CANDIDATE [{r['case_id']}]: {text}")
    elif not has_del:
        print(f"UNKNOWN_NO_DEL [{r['case_id']}]: {text}")

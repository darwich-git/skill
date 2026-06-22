import os
import shutil
import re
import json
import sys

DESKTOP_PATH = r"C:\Users\darwi.PCDARWICH\OneDrive\Desktop"
INBOX_PATH = r"D:\00_EKOSISTEMA_OS\00_INBOX"
VAULT_ROOT = r"D:\00_EKOSISTEMA_OS"

# Known Stock Tickers in Ekosistema
TICKERS = [
    "ALWEC", "APR", "ATD", "BLC", "BLO", "DNP", "GAW", "GOOG", "HCA", "JEN", 
    "JET2", "LTG", "MACF", "MAD", "MBK", "MCEM", "MLG", "NA9", "PLN", "PLX", 
    "SDI", "SIS", "SPR", "TITC", "TOI", "UD", "VBNK", "VLE", "WATR"
]

def is_file_locked(filepath):
    """Checks if a file is locked/open in another application."""
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, 'a'):
            pass
        return False
    except OSError:
        return True

def scan_desktop_to_inbox():
    """Moves all files from Desktop to Inbox, ignoring system files and shortcuts."""
    if not os.path.exists(DESKTOP_PATH):
        return {"status": "error", "message": f"Desktop path does not exist: {DESKTOP_PATH}"}
    if not os.path.exists(INBOX_PATH):
        os.makedirs(INBOX_PATH, exist_ok=True)

    moved_files = []
    skipped_files = []

    for item in os.listdir(DESKTOP_PATH):
        item_path = os.path.join(DESKTOP_PATH, item)
        if os.path.isdir(item_path):
            skipped_files.append({"name": item, "reason": "directory"})
            continue

        if item.lower().endswith(('.lnk', '.ini')) or item.startswith('.') or item.startswith('~'):
            skipped_files.append({"name": item, "reason": "system/shortcut"})
            continue

        if is_file_locked(item_path):
            skipped_files.append({"name": item, "reason": "locked"})
            continue

        dest_path = os.path.join(INBOX_PATH, item)
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(item)
            counter = 1
            while os.path.exists(os.path.join(INBOX_PATH, f"{base}_{counter}{ext}")):
                counter += 1
            dest_path = os.path.join(INBOX_PATH, f"{base}_{counter}{ext}")

        try:
            shutil.move(item_path, dest_path)
            moved_files.append({"original": item, "moved_as": os.path.basename(dest_path)})
        except Exception as e:
            skipped_files.append({"name": item, "reason": f"error: {str(e)}"})

    return {"status": "success", "moved": moved_files, "skipped": skipped_files}

def analyze_inbox():
    """Analyzes the files in Inbox and generates a classification plan with confidence indicators."""
    locked_on_desktop = []
    if os.path.exists(DESKTOP_PATH):
        for item in os.listdir(DESKTOP_PATH):
            item_path = os.path.join(DESKTOP_PATH, item)
            if os.path.isfile(item_path) and not item.lower().endswith(('.lnk', '.ini')) and not item.startswith('.') and not item.startswith('~'):
                if is_file_locked(item_path):
                    locked_on_desktop.append(item)

    plan = []
    
    # Process Desktop locked files first
    for item in locked_on_desktop:
        plan.append({
            "original_name": item,
            "category": "Bloqueado",
            "proposed_dest_rel": "N/A (Bloqueado en Escritorio)",
            "proposed_dest_display": "N/A (Escritorio)",
            "proposed_name": item,
            "rationale": "El archivo está abierto en otra aplicación (ej: Excel). Ciérralo para poder procesarlo.",
            "confidence": "RED",
            "approved": False,
            "on_desktop": True
        })

    if not os.path.exists(INBOX_PATH):
        return {"status": "success", "plan": plan, "files_found": len(plan)}

    for item in os.listdir(INBOX_PATH):
        item_path = os.path.join(INBOX_PATH, item)
        if os.path.isdir(item_path):
            continue
            
        file_name, ext = os.path.splitext(item)
        ext_lower = ext.lower()
        
        # Default fallback
        proposed_dest = "00_INBOX"
        proposed_dest_display = "00_INBOX"
        proposed_name = item
        rationale = "No se ha detectado patrón específico. Permanece en Inbox."
        category = "Otros"
        confidence = "YELLOW"
        
        # 1. Check for Books/Reading (06_MENTE\06.01_Biblioteca)
        if ext_lower in ['.epub', '.mobi', '.azw3'] or (ext_lower == '.pdf' and any(kw in file_name.lower() for kw in ['book', 'libro', 'biografia', 'history', 'manual', 'taleb', 'greenblatt', 'buffett', 'lynch', 'mayer', 'patdorsey', 'marks', 'bernstein', 'paramés', 'bogle', 'wyckoff', 'villahermosa'])):
            category = "06_MENTE/Biblioteca"
            confidence = "GREEN"
            
            subfolder = "06.02_Modelos_Mentales_y_Psicologia"
            if any(kw in file_name.lower() for kw in ['bagger', 'dcf', 'valora', 'invest', 'stock', 'shares', 'finance', 'finanzas', 'accounting', 'arbitrage', 'mckinsey', 'portfolio', 'buffett', 'lynch', 'bogle', 'marks', 'bernstein', 'paramés', 'wyckoff', 'villahermosa']):
                subfolder = "06.01_Inversion_y_Finanzas"
            elif any(kw in file_name.lower() for kw in ['history', 'biography', 'story', 'lee kuan', 'singapore', 'guerra', 'imperio']):
                subfolder = "06.03_Historia_Biografias_y_Estrategia"
            elif any(kw in file_name.lower() for kw in ['bread', 'pan', 'gastronomia', 'receta', 'baker', 'tartine']):
                subfolder = "06.04_Panaderia_y_Gastronomia"
                
            proposed_dest = os.path.join("06_MENTE", "06.01_Biblioteca", subfolder)
            proposed_dest_display = subfolder
            
            # Clean name suggestion
            clean_name = file_name
            clean_name = re.sub(r'\(z-library\.sk.*?\)', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'\(1lib\.sk.*?\)', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'\(z-lib\.sk.*?\)', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'\(z-li.*?\)', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'\(Z-Library\)', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'\(Spanish Edition\)', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'_\d+', '', clean_name)
            clean_name = clean_name.replace('_', ' ').replace('-', ' - ').strip()
            clean_name = re.sub(r'\s*-\s*', ' - ', clean_name)
            clean_name = re.sub(r'\s+', ' ', clean_name)
            proposed_name = f"{clean_name}{ext}"
            rationale = "Libro detectado. Sugerido en Biblioteca con renombrado limpio."

        # 2. Check for Visual Resources (07_RECURSOS_VISUALES)
        elif ext_lower in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
            category = "07_RECURSOS_VISUALES"
            confidence = "GREEN"
            proposed_dest = os.path.join("07_RECURSOS_VISUALES", "07.00_Visual_Inbox")
            proposed_dest_display = "07.00_Visual_Inbox"
            proposed_name = item
            rationale = "Imagen detectada. Enviada a bandeja visual."

        # 3. Check for Ticker Reports / Ekomonos (03_DINERO\03.01_Inversion)
        elif ext_lower == '.pdf' and any(ticker.lower() in file_name.lower() for ticker in TICKERS):
            matched_ticker = next(ticker for ticker in TICKERS if ticker.lower() in file_name.lower())
            category = "03_DINERO/Inversion/Ekomonos"
            confidence = "GREEN"
            
            if any(kw in file_name.lower() for kw in ['transcript', 'call', 'earnings call', 'audio']):
                subfolder = os.path.join("02_Fuentes_Inmutables", "02.02_Transcripciones")
                subfolder_display = f"{matched_ticker} \\ 02.02_Transcripciones"
            elif any(kw in file_name.lower() for kw in ['press', 'release', 'nota', 'news']):
                subfolder = os.path.join("02_Fuentes_Inmutables", "02.03_Articulos_y_Prensa")
                subfolder_display = f"{matched_ticker} \\ 02.03_Articulos_y_Prensa"
            else:
                subfolder = os.path.join("02_Fuentes_Inmutables", "02.01_Reportes")
                subfolder_display = f"{matched_ticker} \\ 02.01_Reportes"
                
            proposed_dest = os.path.join("03_DINERO", "03.01_Inversion", "03.01_Ekomonos_Library", "STOCK", matched_ticker, subfolder)
            proposed_dest_display = subfolder_display
            proposed_name = item
            rationale = f"Reporte de {matched_ticker} detectado. Clasificado en Ekomonos."

        # 4. Check for Checklists, general valuation spreadsheets (including Toya / Nike since user doesn't want auto-creation)
        elif ext_lower in ['.xlsx', '.xlsm', '.pdf'] and any(kw in file_name.lower() for kw in ['modelo', 'valoracion', 'valuation', 'dcf', 'checklist', 'toya', 'nike', 'plantilla']):
            category = "03_DINERO/Inversion/Plantillas"
            confidence = "GREEN"
            proposed_dest = os.path.join("03_DINERO", "03.01_Inversion", "03.04_Playbook_y_Herramientas", "01_Plantillas")
            proposed_dest_display = "01_Plantillas"
            
            # Clean name suggestion
            clean_name = file_name.replace(" ", "_")
            if "toya" in file_name.lower():
                clean_name = "Plantilla_Valoracion_Toya"
            elif "nike" in file_name.lower():
                clean_name = "Nike_Inc"
            elif "checklist" in file_name.lower():
                clean_name = "MI_CHECKLIST_2025_V3"
                
            proposed_name = f"{clean_name}{ext}"
            rationale = "Plantilla u hoja de cálculo de inversión. Ubicada en 01_Plantillas."

        # 5. Check for Trabajo (03_DINERO\03.02_Trabajo)
        elif any(kw in file_name.lower() for kw in ['payslip', 'nomina', 'contrato', 'contract', 'interview', 'entrevista', 'cv', 'curriculum', 'p45', 'scottish water', 'scottiswater']):
            category = "03_DINERO/Trabajo"
            confidence = "GREEN"
            
            if any(kw in file_name.lower() for kw in ['payslip', 'nomina']):
                subfolder = "Nominas"
            elif any(kw in file_name.lower() for kw in ['cv', 'curriculum', 'cover letter', 'presentacion']):
                subfolder = "Curriculums_y_Cartas"
            elif any(kw in file_name.lower() for kw in ['interview', 'entrevista', 'guide', 'preparacion']):
                subfolder = "Entrevistas"
            else:
                subfolder = "Contratos_y_Documentacion"
                
            proposed_dest = os.path.join("03_DINERO", "03.02_Trabajo", subfolder)
            proposed_dest_display = subfolder
            
            proposed_name = item
            if "payslip" in file_name.lower() or "nomina" in file_name.lower():
                date_match = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|diciembre|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre)\b', file_name, re.IGNORECASE)
                year_match = re.search(r'\b(20\d{2})\b', file_name)
                month_str = date_match.group(0).upper() if date_match else "PAYSLIP"
                year_str = year_match.group(0) if year_match else "2026"
                proposed_name = f"SW_Payslip_{month_str}_{year_str}{ext}"
                
            rationale = "Documento laboral detectado. Asignado a Trabajo."

        # 6. Check for Fiscalidad (03_DINERO\03.03_Fiscalidad)
        elif any(kw in file_name.lower() for kw in ['hmrc', 'tax', 'return', 'fiscal', 'ibkr 20', 'tax summary']):
            category = "03_DINERO/Fiscalidad"
            confidence = "GREEN"
            proposed_dest = os.path.join("03_DINERO", "03.03_Fiscalidad")
            proposed_dest_display = "03.03_Fiscalidad"
            proposed_name = item
            rationale = "Declaración o informe fiscal detectado."

        # 7. Check for Contabilidad (03_DINERO\03.04_Contabilidad_Patrimonial)
        elif any(kw in file_name.lower() for kw in ['caxxx', 'bank report', 'net worth', 'patrimonio', 'presupuesto']):
            category = "03_DINERO/Contabilidad"
            confidence = "GREEN"
            proposed_dest = os.path.join("03_DINERO", "03.04_Contabilidad_Patrimonial")
            proposed_dest_display = "03.04_Contabilidad_Patrimonial"
            proposed_name = item
            rationale = "Control financiero patrimonial detectado."

        # 8. Check for Salud (02_SALUD)
        elif any(kw in file_name.lower() for kw in ['analitica', 'medico', 'health', 'suplemento', 'supl', 'doctor', 'receta medica']):
            category = "02_SALUD"
            confidence = "GREEN"
            proposed_dest = "02_SALUD"
            proposed_dest_display = "02_SALUD"
            proposed_name = item
            if "supl" in file_name.lower() or "suplemento" in file_name.lower():
                proposed_name = f"Plan_Suplementos{ext}"
            rationale = "Documentación médica o suplementos detectados."

        # 9. Check for Infraestructura (04_INFRAESTRUCTURA)
        elif any(kw in file_name.lower() for kw in ['alquiler', 'rent', 'lease', 'hipoteca', 'mortgage', 'hamburg', 'cuesta calderon', 'vehi', 'coche', 'garantia', 'ticket', 'sierra', 'factura', 'invoice']):
            category = "04_INFRAESTRUCTURA"
            confidence = "GREEN"
            
            if "hamburg" in file_name.lower():
                subfolder = "04.01_Hamburg_Place"
            elif "cuesta calderon" in file_name.lower():
                subfolder = "04.02_Cuesta_Calderon"
            elif any(kw in file_name.lower() for kw in ['vehi', 'coche', 'car']):
                subfolder = "04.03_Vehiculos"
            elif any(kw in file_name.lower() for kw in ['garantia', 'ticket', 'sierra', 'receipt']):
                subfolder = "04.04_Garantias_y_Tickets_Generales"
            else:
                subfolder = ""
                
            proposed_dest = os.path.join("04_INFRAESTRUCTURA", subfolder)
            proposed_dest_display = subfolder if subfolder else "04_INFRAESTRUCTURA"
            proposed_name = item
            rationale = "Documento o factura de infraestructura detectado."

        # 10. Check for Familia (05_FAMILIA)
        elif any(kw in file_name.lower() for kw in ['lia', 'familia', 'compra', 'nacimiento', 'pasaporte lia']):
            category = "05_FAMILIA"
            confidence = "GREEN"
            proposed_dest = os.path.join("05_FAMILIA", "Lia")
            proposed_dest_display = "Lia"
            proposed_name = item
            rationale = "Registro o papeles de Lia/Familia."

        plan.append({
            "original_name": item,
            "category": category,
            "proposed_dest_rel": proposed_dest,
            "proposed_dest_display": proposed_dest_display,
            "proposed_name": proposed_name,
            "rationale": rationale,
            "confidence": confidence,
            "register_new_company": False,
            "approved": True,
            "on_desktop": False
        })
        
    return {"status": "success", "plan": plan, "files_found": len(plan)}

def execute_plan(plan_file_path):
    """Executes the approved moves and renamings."""
    if not os.path.exists(plan_file_path):
        return {"status": "error", "message": f"Plan file not found: {plan_file_path}"}
        
    with open(plan_file_path, "r", encoding="utf-8") as f:
        plan_data = json.load(f)
        
    results = []
    
    for item in plan_data:
        if not item.get("approved", True):
            results.append({"original": item["original_name"], "status": "skipped", "reason": "No aprobado por el usuario"})
            continue
            
        src_path = os.path.join(INBOX_PATH, item["original_name"])
        if item.get("on_desktop", False):
            src_path = os.path.join(DESKTOP_PATH, item["original_name"])

        if not os.path.exists(src_path):
            results.append({"original": item["original_name"], "status": "error", "reason": "El archivo de origen ya no existe"})
            continue
            
        if is_file_locked(src_path):
            results.append({"original": item["original_name"], "status": "error", "reason": "El archivo está abierto por otro programa"})
            continue

        dest_dir = os.path.join(VAULT_ROOT, item["proposed_dest_rel"])
        os.makedirs(dest_dir, exist_ok=True)
        
        dest_path = os.path.join(dest_dir, item["proposed_name"])
        
        if os.path.exists(dest_path) and dest_path != src_path:
            base, ext = os.path.splitext(item["proposed_name"])
            counter = 1
            while os.path.exists(os.path.join(dest_dir, f"{base}_{counter}{ext}")):
                counter += 1
            dest_path = os.path.join(dest_dir, f"{base}_{counter}{ext}")
            
        try:
            shutil.move(src_path, dest_path)
            results.append({
                "original": item["original_name"],
                "dest_rel": os.path.relpath(dest_path, VAULT_ROOT),
                "status": "success"
            })
        except Exception as e:
            results.append({"original": item["original_name"], "status": "error", "reason": str(e)})
            
    files_moved = sum(1 for r in results if r["status"] == "success")
    return {"status": "success", "results": results, "files_found": len(plan_data), "files_moved": files_moved}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No action specified."}))
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == "scan_desktop":
        result = scan_desktop_to_inbox()
        print(json.dumps(result, indent=2))
        
    elif action == "analyze_inbox":
        result = analyze_inbox()
        print(json.dumps(result, indent=2))
        
    elif action == "execute_plan":
        if len(sys.argv) < 3:
            print(json.dumps({"status": "error", "message": "Missing plan file path."}))
            sys.exit(1)
        plan_file = sys.argv[2]
        result = execute_plan(plan_file)
        print(json.dumps(result, indent=2))
        
    else:
        print(json.dumps({"status": "error", "message": f"Unknown action: {action}"}))

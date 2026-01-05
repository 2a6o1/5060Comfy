#!/bin/bash

# ============================================================================
# CONFIGURACIÓN - VARIABLES DE ENTORNO
# ============================================================================
set -euo pipefail  # Fallar rápido en errores

# Rutas base (centralizadas para fácil modificación)
BASE_DIR="/myfiles/ssd/stuff"
SOFTWARE_DIR="$BASE_DIR/software"
ENVS_DIR="$BASE_DIR/envs"
PROJECTS_DIR="$BASE_DIR/projects"
CACHE_DIR="$BASE_DIR/cache"
OUTPUTS_DIR="$BASE_DIR/outputs"
TEMP_DIR="$BASE_DIR/temp"

# Rutas específicas
MINIFORGE_PATH="$SOFTWARE_DIR/miniforge3"
COMFYUI_ENV="$ENVS_DIR/comfyui"
COMFYUI_PROJECT="$PROJECTS_DIR/ComfyUI"
COMFYUI_OUTPUTS="$OUTPUTS_DIR/comfyui"

# Configuración de la aplicación
COMFYUI_HOST="0.0.0.0"
COMFYUI_PORT="8188"
CUDA_DEVICE="0"

# Configuración de logging
LOG_DIR="$BASE_DIR/logs"
MAX_LOG_FILES=10  # Mantener solo los últimos N logs

# Variables globales
LOG_FILE=""
SCRIPT_START_TIME=$(date +%s)

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================
setup_logging() {
    # Crear directorio de logs primero
    mkdir -p "$LOG_DIR"
    
    # Configurar archivo de log
    LOG_FILE="$LOG_DIR/comfyui_$(date +%Y%m%d_%H%M%S).log"
    
    # Limpiar logs antiguos
    cleanup_old_logs
    
    # Registrar inicio
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] === INICIANDO COMFYUI ===" >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Script version: 3.0 (con modo memoria)" >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Fecha: $(date)" >> "$LOG_FILE"
}

log_message() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local level=$1
    local message=$2
    
    # Solo intentar escribir en log si el archivo existe
    if [ -n "$LOG_FILE" ] && [ -f "$LOG_FILE" ]; then
        echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    fi
    
    # Mostrar en consola siempre
    echo "[$timestamp] [$level] $message"
}

check_directory() {
    local dir=$1
    local purpose=$2
    
    if [ ! -d "$dir" ]; then
        log_message "WARNING" "Directorio no encontrado: $dir (para: $purpose)"
        mkdir -p "$dir" 2>/dev/null || {
            log_message "ERROR" "No se pudo crear directorio: $dir"
            return 1
        }
        log_message "INFO" "Directorio creado: $dir"
    fi
    return 0
}

validate_environment() {
    log_message "INFO" "=== VALIDACIÓN DEL ENTORNO ==="
    
    # Verificar directorios esenciales
    local essential_dirs=(
        "$MINIFORGE_PATH"
        "$COMFYUI_ENV"
        "$COMFYUI_PROJECT"
    )
    
    for dir in "${essential_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            log_message "ERROR" "Directorio esencial no encontrado: $dir"
            return 1
        fi
    done
    log_message "INFO" "✓ Directorios esenciales verificados"
    
    # Verificar archivos esenciales
    if [ ! -f "$MINIFORGE_PATH/etc/profile.d/conda.sh" ]; then
        log_message "ERROR" "conda.sh no encontrado en Miniforge"
        return 1
    fi
    
    if [ ! -f "$COMFYUI_PROJECT/main.py" ]; then
        log_message "ERROR" "main.py no encontrado en ComfyUI"
        return 1
    fi
    log_message "INFO" "✓ Archivos esenciales verificados"
    
    return 0
}

cleanup_old_logs() {
    if [ -d "$LOG_DIR" ]; then
        local log_count=$(find "$LOG_DIR" -name "comfyui_*.log" -type f 2>/dev/null | wc -l)
        if [ "$log_count" -gt "$MAX_LOG_FILES" ]; then
            local files_to_delete=$((log_count - MAX_LOG_FILES))
            log_message "INFO" "Limpiando $files_to_delete archivos de log antiguos"
            find "$LOG_DIR" -name "comfyui_*.log" -type f 2>/dev/null | sort | head -n "$files_to_delete" | xargs rm -f 2>/dev/null
        fi
    fi
}

# ============================================================================
# INICIALIZACIÓN
# ============================================================================
main() {
    # Configurar logging primero
    setup_logging
    
    # Validar entorno antes de continuar
    if ! validate_environment; then
        log_message "ERROR" "Validación del entorno fallida. Abortando."
        exit 1
    fi
    
    # Crear directorios necesarios
    local required_dirs=(
        "$CACHE_DIR/torch_extensions"
        "$CACHE_DIR/huggingface"
        "$COMFYUI_OUTPUTS"
        "$TEMP_DIR"
    )
    
    for dir in "${required_dirs[@]}"; do
        check_directory "$dir" "uso del sistema" || exit 1
    done
    
    log_message "INFO" "Ubicación ComfyUI: $COMFYUI_PROJECT"
    
    # ============================================================================
    # ACTIVACIÓN DEL ENTORNO
    # ============================================================================
    log_message "INFO" "Activando entorno Miniforge..."
    if [ -f "$MINIFORGE_PATH/etc/profile.d/conda.sh" ]; then
        source "$MINIFORGE_PATH/etc/profile.d/conda.sh"
        conda activate "$COMFYUI_ENV"
        log_message "INFO" "✓ Entorno Conda activado"
    else
        log_message "ERROR" "No se pudo encontrar conda.sh"
        exit 1
    fi
    
    # ============================================================================
    # CONFIGURACIÓN DE VARIABLES DE ENTORNO
    # ============================================================================
    log_message "INFO" "Configurando optimizaciones..."
    
    # Optimizaciones CUDA/NVIDIA
    export NVIDIA_TF32_OVERRIDE=1
    export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"
    export CUDNN_BENCHMARK=1
    export TORCH_CUDNN_V8_API_ENABLED=1
    
    # Optimizaciones CPU
    local cpu_cores=$(nproc)
    export OMP_NUM_THREADS=$cpu_cores
    export MKL_NUM_THREADS=$cpu_cores
    log_message "INFO" "CPU cores configurados: $cpu_cores"
    
    # Configuración de cache
    export TORCH_EXTENSIONS_DIR="$CACHE_DIR/torch_extensions"
    export HF_HOME="$CACHE_DIR/huggingface"
    export XDG_CACHE_HOME="$CACHE_DIR"
    
    # ============================================================================
    # VERIFICACIÓN DEL ENTORNO PYTHON
    # ============================================================================
    cd "$COMFYUI_PROJECT" || {
        log_message "ERROR" "No se pudo cambiar al directorio: $COMFYUI_PROJECT"
        exit 1
    }
    
    log_message "INFO" "✓ Entorno activado"
    log_message "INFO" "📁 Directorio: $(pwd)"
    
    # Verificar Python y dependencias
    python_version=$(python --version 2>&1 || echo "Python no disponible")
    log_message "INFO" "🐍 Python: $python_version"
    
    # Verificar PyTorch y CUDA
    if python -c "import torch; print('PyTorch version:', torch.__version__)" 2>/dev/null; then
        log_message "INFO" "✓ PyTorch importado correctamente"
    else
        log_message "ERROR" "No se pudo importar PyTorch"
        exit 1
    fi
    
    cuda_available=$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "Error al verificar CUDA")
    log_message "INFO" "🔥 PyTorch CUDA disponible: $cuda_available"
    
    if [ "$cuda_available" != "True" ]; then
        log_message "WARNING" "CUDA no disponible. ComfyUI funcionará en CPU (lento)"
    fi
    
    # Verificar GPU específica
    gpu_info=$(python -c "import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')" 2>/dev/null || echo "Error al obtener info GPU")
    log_message "INFO" "🖥️  $gpu_info"
    
    # ============================================================================
    # DETERMINAR MODO DE MEMORIA
    # ============================================================================
    # Obtener modo de memoria del primer argumento (si existe)
    MEMORY_MODE="${1:-normalvram}"
    
    # Validar modo de memoria
    case "$MEMORY_MODE" in
        "lowvram")
            MEMORY_ARG="--lowvram"
            log_message "INFO" "Usando modo: Low VRAM (para GPUs con poca memoria)"
            ;;
        "normalvram")
            MEMORY_ARG="--normalvram"
            log_message "INFO" "Usando modo: Normal VRAM (recomendado para RTX 5060 8GB)"
            ;;
        "highvram")
            MEMORY_ARG="--highvram"
            log_message "INFO" "Usando modo: High VRAM (solo para GPUs con mucha memoria)"
            ;;
        "cpu")
            MEMORY_ARG="--cpu"
            log_message "INFO" "Usando modo: CPU (sin GPU)"
            ;;
        *)
            MEMORY_ARG="--normalvram"
            log_message "WARNING" "Modo '$MEMORY_MODE' no reconocido, usando Normal VRAM por defecto"
            ;;
    esac
    
    # ============================================================================
    # EJECUCIÓN DE COMFYUI
    # ============================================================================
    log_message "INFO" "=== INICIANDO COMFYUI ==="
    log_message "INFO" "🌐 Acceso: http://$COMFYUI_HOST:$COMFYUI_PORT"
    log_message "INFO" "📂 Salidas: $COMFYUI_OUTPUTS"
    log_message "INFO" "🗑️  Temporal: $TEMP_DIR"
    log_message "INFO" "📝 Log: $LOG_FILE"
    log_message "INFO" "💾 Modo memoria: $MEMORY_MODE ($MEMORY_ARG)"
    echo ""
    echo "=============================================="
    echo "🚀 ComfyUI iniciando en modo $MEMORY_MODE..."
    echo "🌐 Abre http://localhost:$COMFYUI_PORT en tu navegador"
    echo "📝 Ver log completo: $LOG_FILE"
    echo "🛑 Presiona Ctrl+C para detener"
    echo "=============================================="
    echo ""
    
    # Capturar señal de interrupción para logging
    trap 'log_message "INFO" "ComfyUI detenido por el usuario"; exit 0' INT TERM
    
    # Ejecutar ComfyUI con el modo de memoria seleccionado
    log_message "INFO" "Ejecutando ComfyUI con parámetros: $MEMORY_ARG --fp16-unet --fp16-vae --fp16-text-enc"
    
    exec python main.py \
        --listen "$COMFYUI_HOST" \
        --port "$COMFYUI_PORT" \
        --cuda-device "$CUDA_DEVICE" \
        $MEMORY_ARG \
        --fp16-unet \
        --fp16-vae \
        --fp16-text-enc \
        --output-directory "$COMFYUI_OUTPUTS" \
        --temp-directory "$TEMP_DIR" \
        2>&1 | while IFS= read -r line; do
            local log_timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            echo "[$log_timestamp] [COMFYUI] $line" | tee -a "$LOG_FILE"
        done
}

# ============================================================================
# MANEJO DE ERRORES GLOBAL
# ============================================================================
handle_error() {
    local exit_code=$?
    local error_line=$1
    
    if [ -n "$LOG_FILE" ] && [ -f "$LOG_FILE" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] Error en línea $error_line, código: $exit_code" >> "$LOG_FILE"
    fi
    
    echo "❌ Error durante la ejecución (línea $error_line, código: $exit_code)" >&2
    if [ -n "$LOG_FILE" ]; then
        echo "📝 Revisa el log: $LOG_FILE" >&2
    fi
    
    exit $exit_code
}

# Configurar trap para errores
trap 'handle_error ${LINENO}' ERR

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================
main "$@"
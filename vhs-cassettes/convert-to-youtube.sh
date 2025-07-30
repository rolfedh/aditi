#!/bin/bash

# convert-to-youtube.sh
# Converts all GIF files in the vhs-cassettes directory to YouTube-compatible MP4 format
# Uses ffmpeg with optimal settings for YouTube uploads

# set -e  # Exit on any error - disabled to prevent early exit on skip logic

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/youtube-ready"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if ffmpeg is installed
check_ffmpeg() {
    if ! command -v ffmpeg &> /dev/null; then
        print_error "ffmpeg is not installed. Please install it first:"
        echo "  Ubuntu/Debian: sudo apt install ffmpeg"
        echo "  macOS: brew install ffmpeg"
        echo "  Windows: Download from https://ffmpeg.org/download.html"
        exit 1
    fi
    
    print_status "ffmpeg found: $(ffmpeg -version | head -n1)"
}

# Create output directory
create_output_dir() {
    if [[ ! -d "$OUTPUT_DIR" ]]; then
        mkdir -p "$OUTPUT_DIR"
        print_status "Created output directory: $OUTPUT_DIR"
    fi
}

# Check if MP4 already exists for a given GIF
mp4_exists() {
    local gif_file="$1"
    local basename=$(basename "$gif_file" .gif)
    local mp4_file="${OUTPUT_DIR}/${basename}.mp4"
    if [[ -f "$mp4_file" ]]; then
        return 0
    else
        return 1
    fi
}

# Convert GIF to MP4 with YouTube-optimized settings
convert_gif_to_mp4() {
    local input_file="$1"
    local basename=$(basename "$input_file" .gif)
    local output_file="${OUTPUT_DIR}/${basename}.mp4"
    
    print_status "Converting: $input_file -> $output_file"
    
    # YouTube-optimized ffmpeg settings:
    # -movflags faststart: Enables fast start for web playback
    # -pix_fmt yuv420p: Compatible pixel format for most players
    # -vf scale: Ensures even dimensions (required by some codecs)
    # -r 30: Set frame rate to 30fps (good for YouTube)
    # -crf 18: High quality compression (lower = better quality)
    # -preset slow: Better compression (slower encoding, smaller file)
    
    if ffmpeg -i "$input_file" \
        -movflags faststart \
        -pix_fmt yuv420p \
        -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
        -r 30 \
        -c:v libx264 \
        -crf 18 \
        -preset slow \
        -y \
        "$output_file" 2>/dev/null; then
        
        # Get file sizes for comparison
        local input_size=$(stat -f%z "$input_file" 2>/dev/null || stat -c%s "$input_file" 2>/dev/null || echo "unknown")
        local output_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null || echo "unknown")
        
        print_success "Converted: $basename.gif"
        if [[ "$input_size" != "unknown" && "$output_size" != "unknown" ]]; then
            local input_mb=$((input_size / 1024 / 1024))
            local output_mb=$((output_size / 1024 / 1024))
            echo "          Size: ${input_mb}MB -> ${output_mb}MB"
        fi
        return 0
    else
        print_error "Failed to convert: $input_file"
        return 1
    fi
}

# Main conversion process
main() {
    print_status "VHS GIF to YouTube MP4 Converter"
    echo "=================================="
    
    check_ffmpeg
    create_output_dir
    
    # Find all GIF files in the current directory
    local gif_files=()
    while IFS= read -r -d '' file; do
        gif_files+=("$file")
    done < <(find "$SCRIPT_DIR" -maxdepth 1 -name "*.gif" -type f -print0)
    
    if [[ ${#gif_files[@]} -eq 0 ]]; then
        print_warning "No GIF files found in $SCRIPT_DIR"
        echo "Generate some GIFs first using VHS:"
        echo "  vhs your-cassette.tape"
        exit 0
    fi
    
    print_status "Found ${#gif_files[@]} GIF file(s) to process"
    echo
    
    local converted=0
    local failed=0
    local skipped=0
    
    for gif_file in "${gif_files[@]}"; do
        if mp4_exists "$gif_file"; then
            local basename=$(basename "$gif_file" .gif)
            print_status "Skipping: $basename.gif (MP4 already exists)"
            ((skipped++))
        else
            if convert_gif_to_mp4 "$gif_file"; then
                ((converted++))
            else
                ((failed++))
            fi
        fi
        echo
    done
    
    # Handle case where all files were skipped
    if [[ $converted -eq 0 && $failed -eq 0 && $skipped -gt 0 ]]; then
        echo
        print_success "All GIF files already converted to MP4!"
        echo "  Total GIFs: ${#gif_files[@]}"
        echo "  Already converted: $skipped"
        echo "  Output directory: $OUTPUT_DIR"
        echo
        echo "📺 Your MP4 files are ready for YouTube upload!"
        return 0
    fi
    
    echo "=================================="
    print_success "Conversion complete!"
    echo "  Total GIFs found: ${#gif_files[@]}"
    echo "  Already converted: $skipped"
    echo "  Newly converted: $converted"
    if [[ $failed -gt 0 ]]; then
        echo "  Failed: $failed files"
    fi
    echo "  Output directory: $OUTPUT_DIR"
    echo
    echo "📺 Your MP4 files are now ready for YouTube upload!"
    echo "💡 Tips for YouTube:"
    echo "   - Use descriptive titles and descriptions"
    echo "   - Add relevant tags and categories"
    echo "   - Consider adding thumbnails"
    echo "   - Check YouTube's upload guidelines"
}

# Help function
show_help() {
    echo "VHS GIF to YouTube MP4 Converter"
    echo
    echo "USAGE:"
    echo "  $0 [OPTIONS]"
    echo
    echo "OPTIONS:"
    echo "  -h, --help     Show this help message"
    echo "  -o, --output   Specify output directory (default: ./youtube-ready)"
    echo
    echo "DESCRIPTION:"
    echo "  Converts GIF files in the current directory to YouTube-compatible MP4 format"
    echo "  using optimal settings for web playback and quality. Skips GIFs that already"
    echo "  have matching MP4 files to avoid redundant processing."
    echo
    echo "REQUIREMENTS:"
    echo "  - ffmpeg must be installed and available in PATH"
    echo
    echo "EXAMPLES:"
    echo "  $0                    # Convert all GIFs in current directory"
    echo "  $0 -o /tmp/videos     # Convert with custom output directory"
    echo
    echo "OUTPUT:"
    echo "  MP4 files will be created in ./youtube-ready/ directory"
    echo "  Original GIF files are not modified"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Run the main function
main "$@"
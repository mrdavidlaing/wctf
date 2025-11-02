# Hugo site build and deployment
# Cross-platform Makefile (requires: make, curl, gh CLI)
.PHONY: build serve clean fetch-resume publish-gist onepage-pdf engineering-pdf clean-resume dev help

GIST_ID = c88b3618a13d662c6007c658646ed2f0
GIST_URL = https://gist.githubusercontent.com/mrdavidlaing/$(GIST_ID)/raw/resume.json
RESUME_FILE = static/resume.json

# Default target
all: build

# Development workflow (no external dependencies)
dev:
	hugo server -D --bind 0.0.0.0

# Fetch latest resume from GitHub Gist using curl
fetch-resume:
	@echo "📥 Fetching latest resume.json from GitHub Gist..."
	curl -f -s -o $(RESUME_FILE) $(GIST_URL) && echo "✅ Successfully updated resume.json" || (echo "❌ Failed to fetch resume.json" && exit 1)

# Publish local resume.json to GitHub Gist using gh CLI
publish-gist:
	@echo "🚀 Publishing resume.json to GitHub Gist..."
	@test -f $(RESUME_FILE) || (echo "❌ File not found: $(RESUME_FILE)" && exit 1)
	gh gist edit $(GIST_ID) $(RESUME_FILE) --filename resume.json && echo "✅ Successfully published resume.json to Gist!" || (echo "❌ Failed to publish to Gist" && exit 1)

# Generate PDF resume using onepage-updated theme (compact, print-friendly)
# Usage: make onepage-pdf [SOURCE=path/to/resume.json] [DEST=output/path.pdf]
# Defaults: SOURCE=static/resume.json, DEST=static/resume.pdf
onepage-pdf:
	$(eval SOURCE ?= static/resume.json)
	$(eval DEST ?= static/resume.pdf)
	@echo "📄 Generating PDF resume using onepage-updated theme..."
	@echo "  Source: $(SOURCE)"
	@echo "  Destination: $(DEST)"
	npx -p resumed -p jsonresume-theme-onepage-updated -p puppeteer resumed export "$(SOURCE)" -t jsonresume-theme-onepage-updated -o "$(DEST)"
	@echo "✅ Resume PDF generated successfully at $(DEST)!"

# Generate PDF resume using RenderCV engineering theme (academic/technical CV)
# Usage: make engineering-pdf [SOURCE=path/to/resume.json] [DEST=output/path.pdf]
# Defaults: SOURCE=static/resume.json, DEST=static/resume.pdf
engineering-pdf:
	$(eval SOURCE ?= static/resume.json)
	$(eval DEST ?= static/resume.pdf)
	@echo "📄 Converting JSON Resume to RenderCV YAML format..."
	@echo "  Source: $(SOURCE)"
	@echo "  Destination: $(DEST)"
	@uvx --with pyyaml python scripts/json-to-rendercv.py "$(SOURCE)"
	@echo "📁 Moving YAML file to static directory..."
	mv resume.yaml static/resume.yaml
	@echo "🎨 Generating PDF with RenderCV (engineering theme)..."
	uvx --from 'rendercv[full]' rendercv render static/resume.yaml --output-folder-name .tmp/rendercv_output
	@echo "📁 Copying PDF to destination..."
	cp ".tmp/rendercv_output/David_Laing_CV.pdf" "$(DEST)"
	@echo "✅ Resume PDF generated successfully at $(DEST)!"

# Clean resume generation artifacts (keeps static/resume.yaml)
clean-resume:
	@echo "🧹 Cleaning resume generation artifacts..."
	rm -f resume.yaml
	rm -rf .tmp/rendercv_output/
	@echo "✅ Resume artifacts cleaned! (static/resume.yaml preserved)"

# Build the site
build:
	hugo --minify

# Serve development server
serve:
	hugo server -D --bind 0.0.0.0

# Clean build artifacts
clean:
	rm -rf public/

# Show help
help:
	@echo "Cross-platform Hugo site commands:"
	@echo ""
	@echo "Development:"
	@echo "  dev          - Start development server (no external deps)"
	@echo "  serve        - Start development server"
	@echo "  build        - Build the site"
	@echo "  clean        - Remove build artifacts"
	@echo ""
	@echo "Resume management:"
	@echo "  fetch-resume   - Fetch latest resume.json from GitHub Gist"
	@echo "  publish-gist   - Publish local resume.json to GitHub Gist"
	@echo "  onepage-pdf    - Generate PDF using onepage-updated theme (compact, print-friendly)"
	@echo "                 Usage: make onepage-pdf [SOURCE=path/to/resume.json] [DEST=output.pdf]"
	@echo "  engineering-pdf - Generate PDF using RenderCV engineering theme (academic/technical)"
	@echo "                 Usage: make engineering-pdf [SOURCE=path/to/resume.json] [DEST=output.pdf]"
	@echo "  clean-resume   - Clean resume generation artifacts"
	@echo ""
	@echo "Requirements: make, curl, gh CLI, node/npm, uvx"
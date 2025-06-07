# Workshop Framework

A comprehensive tooling framework for building and deploying interactive workshops quickly and efficiently. This framework provides a complete solution for creating educational content with integrated development environments, automated deployment to cloud platforms, and streamlined workshop management.

## Features

- **Quick Workshop Setup**: Initialize workshop projects with pre-configured templates
- **Integrated Development Environment**: Built-in Jupyter notebooks, VSCode, and terminal access
- **Docker-based Deployment**: Containerized environments for consistent workshop experiences
- **GitHub Integration**: Automated CI/CD pipelines for seamless publishing
- **Brev Cloud Publishing**: Direct integration with Brev.dev for cloud-based workshop delivery
- **Customizable Environment**: Flexible Dockerfile and compose configurations
- **Interactive Lab Manuals**: Markdown-based documentation with navigation and static assets

## Prerequisites

- **Docker**: Install Docker on your system for containerized workshop environments
    - Windows/Mac: [Rancher Desktop](https://rancherdesktop.io/) (recommended) or [Docker Desktop](https://www.docker.com/products/docker-desktop/)
    - Linux: [Docker Engine](https://docs.docker.com/engine/install/)
- **Python 3.10+**: Required for running the framework tools
- **Git**: For version control and GitHub integration
- **pipx** *(Optional but Recommended)*: For isolated tool installation
    - Windows: `python3 -m pip install --user pipx`
    - Mac: `brew install pipx`
    - Linux: `python3 -m pip install --user pipx`

## Installation

### Method 1: Using pipx (Recommended)

```bash
pipx install git+https://github.com/rmkraus/workshop-framework.git
devx --help
```

### Method 2: Using pip

```bash
pip install git+https://github.com/rmkraus/workshop-framework.git
devx --help
```

### Method 3: Development Installation

For framework development or customization:

```bash
git clone https://github.com/rmkraus/workshop-framework.git
cd workshop-framework
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
devx --help
```

## Quick Start Guide

### 1. Create a GitHub Repository

Create a **public** GitHub repository for your workshop. The framework requires GitHub for publishing capabilities.

**Important**: Configure repository permissions for container publishing:
1. Go to your repository's **Settings**
2. Navigate to **Actions** → **General**
3. Under **Workflow permissions**, select **Read and write permissions**
4. Click **Save**

### 2. Initialize Your Workshop

```bash
# Clone your repository
git clone git@github.com:yourusername/your-workshop.git
cd your-workshop

# Initialize workshop structure
devx devel init

# Start local development
devx workshop start
```

### 3. Customize Your Workshop

Edit the generated files to match your workshop requirements:

- **`pyproject.toml`**: Project metadata and configuration
- **`Dockerfile`**: Custom environment setup and dependencies
- **`.devx/`**: Lab manual content and navigation

## Project Structure

After initialization, your workshop will have the following structure:

```
your-workshop/
├── .devx/                    # Lab manual and configuration
│   ├── README.md             # Landing page content
│   ├── _sidebar.md           # Navigation structure
│   ├── _static/              # Images and static assets
│   ├── index.html            # Web interface template
│   ├── jp_app_launcher.yaml  # Jupyter launcher config
│   ├── compose.yaml          # Auto-generated Docker compose
│   ├── compose.local.yaml    # Local development compose (ignored by git)
│   └── *.md                  # Additional manual pages
├── Dockerfile                # Environment configuration
├── pyproject.toml            # Project metadata
├── variables.env             # Environment variables
├── README.md                 # Project documentation
└── [your-content]/           # Workshop materials and code
```

## Command Reference

The Workshop Framework CLI is organized into logical command groups for better organization and discoverability. Use `devx --help` to see all available command groups, or `devx <group> --help` to see commands within a specific group.

### Development Commands
- **`devx devel init`**: Initialize a new workshop in the current directory
- **`devx devel sync`**: Update Docker compose files with latest configuration

### Workshop Management Commands
- **`devx workshop start`**: Start the workshop environment locally
- **`devx workshop stop`**: Stop the workshop environment
- **`devx workshop build`**: Build the workshop container
- **`devx workshop restart`**: Restart the workshop environment
- **`devx workshop status`**: Check the status of workshop containers

### Publishing Commands
- **`devx publish brev`**: Deploy workshop to Brev.dev cloud platform

### General
- **`devx --help`**: Display all available commands and options

## Customization Guide

### Environment Configuration

The `Dockerfile` is fully customizable but includes essential framework components. You can:
- Add additional software packages
- Install Python/R/other language dependencies
- Configure environment variables
- Set up custom services

### Lab Manual Content

Edit files in the `.devx/` directory:
- Use Markdown for content creation
- Add images and files to `_static/`
- Update `_sidebar.md` for navigation structure
- Customize `index.html` for branding

### Workshop Materials

Organize your workshop content in the root directory:
- Jupyter notebooks (`.ipynb`)
- Python scripts and modules
- Data files and datasets
- Documentation and resources

## Local Development

### Starting Your Workshop

```bash
devx workshop start
```

This command will:
1. Build the Docker container
2. Start all required services
3. Open the workshop interface in your browser

### Development Workflow

1. Make changes to your workshop content
2. Test locally using `devx workshop start`
3. Synchronize configuration with `devx devel sync`
4. Commit and push changes to GitHub
5. Publish to cloud with `devx publish brev`

## Troubleshooting

### Common Issues

**Workshop fails to start:**
```bash
# Check container status
docker ps -a

# View container logs
docker logs devx-devx-1

# Access container shell for debugging
docker exec -it devx-devx-1 /bin/bash
```

**Port conflicts:**
- Stop other services using ports 8888 (Jupyter) or 3000 (VSCode)
- Modify port mappings in compose files if needed

**Permission issues:**
- Ensure Docker is running with appropriate permissions
- Check file ownership in mounted volumes

### Getting Help

- Check the [GitHub Issues](https://github.com/rmkraus/workshop-framework/issues) for known problems
- Review Docker and container logs for specific error messages
- Ensure all prerequisites are properly installed

## Publishing Workshops

### Prepare for Publishing

1. Test your workshop thoroughly with `devx workshop start`
2. Update documentation and README files
3. Synchronize configurations: `devx devel sync`
4. Commit all changes to your repository

```bash
git add -A
git commit -m "Ready for publication"
git push origin main
```

### Deploy to Brev.dev

```bash
devx publish brev
```

This will:
- Validate your workshop configuration
- Build and push container images
- Create a Brev.dev launchable
- Provide access URLs for participants

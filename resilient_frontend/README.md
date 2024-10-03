# Resilient Frontend
<div align="center">
  <a href="https://angular.io/" target="_blank">
    <img src="https://img.shields.io/badge/Angular-%23c3002f?logo=angular" alt="Angular">
  </a>
  <a href="https://nodejs.org/" target="_blank">
    <img src="https://img.shields.io/badge/Node-333333?logo=nodedotjs" alt="Node">
  </a>
  <a href="https://www.docker.com/" target="_blank">
    <img src="https://img.shields.io/badge/Docker-%23384d54?logo=docker" alt="Docker">
  </a>
  <a href="https://material.angular.io/" target="_blank">
    <img src="https://img.shields.io/badge/Angular%20material-FA8B00?logo=materialdesign&logoColor=white" alt="Angular Material">
  </a>
</div>

### This module is aimed at managing the web application (frontend).

The web application is built using Angular and node 18. The source code is under the **src folder** with the following structure:

```markdown
src
├── app (contains the main code)
│   ├── modules
│   │   └── auth
│   │   └── dashboard
│   │   └── landing
│   └── services (general purpose services)
│   └── shared (general puporse libraries and elements)
├── assets (icons, logs, and env files)
└── ...
```


## <a name="requirements"></a> 📋 Requirements

- Node v18.18.2
- NPM v9.8.1

> [!NOTE]
> The previous Node and NPM versions where used to develop the application. Other versions may work but they are not tested.


## <a name="installation"></a> 🔄 Installation

1. Open a terminal in this module's root
2. Install dependencies

```bash
npm install
```

## <a name="run"></a> 🚀 Run

Run the application in development mode

```bash
npm start 
```

## <a name="build"></a> 📦 Build

Production distribution

```bash
npm run build
```

## <a name="docker"></a> 🐳 Docker

### Build the image

> [!WARNING]
> Ensure you are in the 📁 root directory before executing the next command.

- Production image

```bash
docker build -t <target> -f ./docker/frontend/Dockerfile .
```

> where `<target>` is the name of the image to be created. The pattern used is `<registry>/<image-name>:<tag>`


### Push the image

Push the image to the registry

```bash
docker push <image>
```
> Where `<image>` is the name of the image to be pushed.

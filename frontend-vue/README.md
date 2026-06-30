
## Frontend - Versión Vue 3

El directorio `frontend-vue/` contiene un frontend moderno construido con **Vue 3 + Vite**, que consume la API REST con soporte completo para autenticación JWT.


## Autores

| Autor | Porcentaje |
|---------|----------|
| Davis Arapa Chua  | 100 % |
| Sebastian Castro Mamani | 100 % |
| Piero Delgado Chipana | 100 % |
| Hugo Diaz Chavez | 100 % |


### Librerías Utilizadas

#### Dependencias Principales

| Librería | Versión | Descripción | Propósito |
|----------|---------|-------------|----------|
| **Vue** | ^3.5.38 | Framework progresivo JavaScript | Construcción de componentes reactivos y UI interactiva |
| **Vue Router** | ^5.1.0 | Sistema de enrutamiento | Navegación entre vistas (Login, Dashboard) con guards |
| **Pinia** | ^3.0.4 | Gestión centralizada de estado | Store reactivo para autenticación y datos globales |
| **Axios** | ^1.18.0 | Cliente HTTP moderno | Peticiones a la API REST con interceptadores |
| **Vite** | ^8.0.16 | Empaquetador y servidor de desarrollo | Build rápido, HMR (Hot Module Replacement), optimizaciones |

#### Dependencias de Desarrollo

| Librería | Versión | Descripción |
|----------|---------|-------------|
| **@vitejs/plugin-vue** | ^6.0.7 | Plugin oficial de Vite para Vue SFC |
| **vite-plugin-vue-devtools** | ^8.1.2 | Herramientas de desarrollo integradas en Vite |

#### Explicación Detallada

**Vue 3**
- Framework reactivo que permite crear interfaces dinámicas
- Utiliza Composition API y `<script setup>` para código más limpio
- Gestión automática de dependencias en el template

**Vue Router**
- Define rutas como `/login` y `/dashboard`
- Implementa guards (`beforeEach`) para proteger rutas
- Redirige automáticamente a login si falta autenticación

**Pinia**
- Reemplaza Vuex (más simple y eficiente)
- Store `auth.js` mantiene estado de: usuario, token, rol
- Acceso reactivo a datos globales desde cualquier componente

**Axios**
- Intercepción automática de errores 401 (token expirado)
- Adjunta `Authorization: Bearer <token>` en cada petición
- Manejo centralizado de errores HTTP

**Vite**
- Servidor de desarrollo con HMR (cambios instantáneos)
- Build optimizado para producción
- Mucho más rápido que Webpack

---

## Guía de Instalación y Configuración - Frontend Vue

### Requisitos Previos

- **Node.js**: versión 22.18.0 o superior (ver `package.json`)
- **npm**: versión 10+ (incluido con Node.js)
- **Backend Django**: Ejecutándose en `http://127.0.0.1:8000`
- **Git**: Para clonar el repositorio

### Paso 1: Verificar Versión de Node.js

```powershell
node --version
npm --version
```

Salida esperada:
```
v22.18.0 (o superior)
10.x.x (o superior)
```

Si necesitas actualizar Node.js, descárgalo desde [nodejs.org](https://nodejs.org/)

### Paso 2: Navegar al Directorio Frontend

```powershell
cd frontend-vue
```

### Paso 3: Instalar Dependencias

```powershell
npm install
```

Este comando:
- Lee `package.json`
- Descarga todas las librerías necesarias
- Las guarda en la carpeta `node_modules/`
- Genera `package-lock.json` (garantiza versiones exactas)

**Tiempo estimado**: 2-3 minutos en primera instalación

### Paso 4: Configurar la URL de la API

Abre el archivo `src/services/api.js` y verifica:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api';
```

Si tu backend está en otro host/puerto, actualiza esta URL.

### Paso 5: Iniciar el Servidor de Desarrollo

```powershell
npm run dev
```

Salida esperada:
```
VITE v8.0.16  ready in 1234 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### Paso 6: Acceder a la Aplicación

Abre tu navegador y ve a: **`http://localhost:5173`**

Verás la pantalla de login. Usa las credenciales del superusuario:

| Campo | Valor |
|-------|-------|
| Usuario | `admin`  |
| Contraseña | `1234` |

### Estructura de Carpetas del Frontend

```
frontend-vue/
├── package.json                   # Configuración y dependencias
├── package-lock.json              # Lock de versiones
├── vite.config.js                 # Configuración de Vite
├── jsconfig.json                  # Configuración de JavaScript
├── index.html                     # HTML principal
├── public/                        # Assets públicos (favicon, etc)
├── src/
│   ├── main.js                    # Punto de entrada
│   ├── App.vue                    # Componente raíz
│   ├── router/
│   │   └── index.js               # Definición de rutas
│   ├── services/
│   │   └── api.js                 # Cliente HTTP con Axios
│   ├── stores/
│   │   └── auth.js                # Store Pinia para autenticación
│   └── views/
│       ├── LoginView.vue          # Pantalla de login
│       └── DashboardView.vue      # Dashboard principal
└── dist/                          # Output del build (generado)
```

## Rutas del Frontend (Vistas Disponibles)

Acceso desde la barra de navegación o directamente por URL:

| Ruta | Componente | Descripción | Requiere Auth |
|------|-----------|-------------|--------------|
| `/login` | LoginView.vue | Página de autenticación | No |
| `/` | DashboardView.vue | Dashboard principal con estadísticas |  Deshabilitado* |
| `/peluquerias` | PeluceriasView.vue | Lista y gestión de peluquerías |  Deshabilitado* |
| `/usuarios` | UsuariosView.vue | Lista de usuarios con roles |  Deshabilitado* |
| `/estilistas` | EstilistasView.vue | Lista de estilistas y especialidades | Deshabilitado* |
| `/servicios` | ServiciosView.vue | Catálogo de servicios disponibles |  Deshabilitado* |
| `/citas` | CitasView.vue | Gestión de citas y reservas | Deshabilitado* |
| `/horarios` | HorariosView.vue | Horarios de trabajo de estilistas |  Deshabilitado* |

*En desarrollo, la autenticación está deshabilitada (`AllowAny` en Django). Para producción, cambiar a `IsAuthenticated`.


---

## Notas de Seguridad

**En desarrollo:** Se ha deshabilitado la autenticación JWT para facilitar testing.

**Para producción:**
1. Cambiar `DEFAULT_PERMISSION_CLASSES` en `settings.py` a `IsAuthenticated`
2. Usar tokens JWT con expiración corta (15-30 minutos)
3. Implementar refresh tokens
4. Usar HTTPS obligatorio
5. Configurar CORS solo para dominios autorizados

---

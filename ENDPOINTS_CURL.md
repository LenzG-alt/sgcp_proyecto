# Endpoints curl - Sistema de Gestión de Citas para Peluquería (SGCP)

> **NOTA**: En desarrollo, los endpoints son **públicos (AllowAny)** y no requieren autenticación JWT.
> Para producción, cambiar `DEFAULT_PERMISSION_CLASSES` a `IsAuthenticated` en `settings.py`.

---

## 📋 Tabla de Contenidos

1. [Peluquerías](#peluquerías)
2. [Usuarios](#usuarios)
3. [Estilistas](#estilistas)
4. [Servicios](#servicios)
5. [Citas](#citas)
6. [Horarios de Estilistas](#horarios-de-estilistas)
7. [Datos Anidados](#datos-anidados)

---

## 🏢 Peluquerías

### Listar todas las peluquerías

```bash
curl -X GET http://127.0.0.1:8000/api/peluquerias/ \
  -H "Content-Type: application/json"
```

**Respuesta exitosa (200 OK)**:
```json
[
  {
    "id": 1,
    "nombre": "Bella Estética Centro",
    "direccion": "Calle Principal 123, Piso 2",
    "telefono": "555-1234567",
    "descripcion": "Peluquería de lujo en el centro de la ciudad",
    "status": "active",
    "created": "2024-01-15T10:30:00Z",
    "modified": "2024-01-15T10:30:00Z"
  }
]
```

### Obtener una peluquería específica

```bash
curl -X GET http://127.0.0.1:8000/api/peluquerias/1/ \
  -H "Content-Type: application/json"
```

### Crear una nueva peluquería

```bash
curl -X POST http://127.0.0.1:8000/api/peluquerias/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bella Estética Sucursal 2",
    "direccion": "Avenida Secundaria 456",
    "telefono": "555-9876543",
    "descripcion": "Segunda sucursal en zona norte",
    "status": "active"
  }'
```

### Actualizar una peluquería

```bash
curl -X PUT http://127.0.0.1:8000/api/peluquerias/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bella Estética Centro - Actualizado",
    "direccion": "Calle Principal 123, Piso 2",
    "telefono": "555-1234567",
    "descripcion": "Peluquería premium con nuevos servicios",
    "status": "active"
  }'
```

### Eliminar una peluquería

```bash
curl -X DELETE http://127.0.0.1:8000/api/peluquerias/1/ \
  -H "Content-Type: application/json"
```

---

## 👥 Usuarios

### Listar todos los usuarios

```bash
curl -X GET http://127.0.0.1:8000/api/usuarios/ \
  -H "Content-Type: application/json"
```

### Filtrar usuarios por rol

```bash
# Clientes
curl -X GET http://127.0.0.1:8000/api/usuarios/?rol=cliente \
  -H "Content-Type: application/json"

# Administradores
curl -X GET http://127.0.0.1:8000/api/usuarios/?rol=administrador \
  -H "Content-Type: application/json"

# Recepcionistas
curl -X GET http://127.0.0.1:8000/api/usuarios/?rol=recepcionista \
  -H "Content-Type: application/json"
```

### Obtener un usuario específico

```bash
curl -X GET http://127.0.0.1:8000/api/usuarios/1/ \
  -H "Content-Type: application/json"
```

### Crear un nuevo usuario

```bash
curl -X POST http://127.0.0.1:8000/api/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez García",
    "email": "juan.perez@gmail.com",
    "password": "segura123",
    "telefono": "555-1111111",
    "rol": "cliente",
    "status": "active"
  }'
```

### Crear un recepcionista

```bash
curl -X POST http://127.0.0.1:8000/api/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "María López Rodríguez",
    "email": "maria.lopez@bellaestetica.com",
    "password": "admin123",
    "telefono": "555-2222222",
    "rol": "recepcionista",
    "status": "active"
  }'
```

### Actualizar un usuario

```bash
curl -X PUT http://127.0.0.1:8000/api/usuarios/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Carlos Pérez García",
    "email": "juan.carlos@gmail.com",
    "telefono": "555-3333333",
    "rol": "cliente",
    "status": "active"
  }'
```

### Eliminar un usuario

```bash
curl -X DELETE http://127.0.0.1:8000/api/usuarios/1/ \
  -H "Content-Type: application/json"
```

---

## 💇 Estilistas

### Listar todos los estilistas

```bash
curl -X GET http://127.0.0.1:8000/api/estilistas/ \
  -H "Content-Type: application/json"
```

### Obtener un estilista específico

```bash
curl -X GET http://127.0.0.1:8000/api/estilistas/1/ \
  -H "Content-Type: application/json"
```

### Crear un nuevo estilista

```bash
curl -X POST http://127.0.0.1:8000/api/estilistas/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Sofia Mendez",
    "especialidad": "Cortes y Peinados",
    "telefono": "555-4444444",
    "hair_salon": 1,
    "status": "active"
  }'
```

### Estilista especializado en colorimetría

```bash
curl -X POST http://127.0.0.1:8000/api/estilistas/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Alejandra Flores",
    "especialidad": "Colorimetría y Tratamientos",
    "telefono": "555-5555555",
    "hair_salon": 1,
    "status": "active"
  }'
```

### Actualizar un estilista

```bash
curl -X PUT http://127.0.0.1:8000/api/estilistas/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Sofia Mendez Actualizado",
    "especialidad": "Cortes, Peinados y Tratamientos",
    "telefono": "555-4444444",
    "hair_salon": 1,
    "status": "active"
  }'
```

### Eliminar un estilista

```bash
curl -X DELETE http://127.0.0.1:8000/api/estilistas/1/ \
  -H "Content-Type: application/json"
```

---

## ✂️ Servicios

### Listar todos los servicios

```bash
curl -X GET http://127.0.0.1:8000/api/servicios/ \
  -H "Content-Type: application/json"
```

### Obtener un servicio específico

```bash
curl -X GET http://127.0.0.1:8000/api/servicios/1/ \
  -H "Content-Type: application/json"
```

### Crear un nuevo servicio

```bash
curl -X POST http://127.0.0.1:8000/api/servicios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Corte de Cabello",
    "descripcion": "Corte profesional con técnicas modernas",
    "precio": "35.00",
    "duracion_minutos": 45,
    "hair_salon": 1,
    "status": "active"
  }'
```

### Crear más servicios

```bash
# Colorimetría
curl -X POST http://127.0.0.1:8000/api/servicios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Colorimetría",
    "descripcion": "Tinte profesional con productos de calidad",
    "precio": "60.00",
    "duracion_minutos": 90,
    "hair_salon": 1,
    "status": "active"
  }'

# Peinado
curl -X POST http://127.0.0.1:8000/api/servicios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Peinado",
    "descripcion": "Peinado para ocasiones especiales",
    "precio": "50.00",
    "duracion_minutos": 60,
    "hair_salon": 1,
    "status": "active"
  }'

# Tratamiento capilar
curl -X POST http://127.0.0.1:8000/api/servicios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Tratamiento Capilar",
    "descripcion": "Tratamiento intensivo para cabello seco y dañado",
    "precio": "45.00",
    "duracion_minutos": 50,
    "hair_salon": 1,
    "status": "active"
  }'
```

### Actualizar un servicio

```bash
curl -X PUT http://127.0.0.1:8000/api/servicios/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Corte de Cabello Premium",
    "descripcion": "Corte profesional con técnicas modernas - versión premium",
    "precio": "50.00",
    "duracion_minutos": 60,
    "hair_salon": 1,
    "status": "active"
  }'
```

### Eliminar un servicio

```bash
curl -X DELETE http://127.0.0.1:8000/api/servicios/1/ \
  -H "Content-Type: application/json"
```

---

## 📅 Citas

### Listar todas las citas

```bash
curl -X GET http://127.0.0.1:8000/api/citas/ \
  -H "Content-Type: application/json"
```

### Filtrar citas por estado

```bash
curl -X GET http://127.0.0.1:8000/api/citas/?estado=confirmada \
  -H "Content-Type: application/json"
```

### Obtener una cita específica

```bash
curl -X GET http://127.0.0.1:8000/api/citas/1/ \
  -H "Content-Type: application/json"
```

### Crear una nueva cita

```bash
curl -X POST http://127.0.0.1:8000/api/citas/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "stylist": 1,
    "service": 1,
    "fecha": "2024-02-20",
    "hora_inicio": "10:00:00",
    "hora_fin": "10:45:00",
    "estado": "pendiente",
    "observaciones": "Cliente nuevo, primera vez en el salón"
  }'
```

### Crear múltiples citas

```bash
# Cita 2
curl -X POST http://127.0.0.1:8000/api/citas/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": 2,
    "stylist": 2,
    "service": 2,
    "fecha": "2024-02-21",
    "hora_inicio": "14:00:00",
    "hora_fin": "15:30:00",
    "estado": "confirmada",
    "observaciones": "Cliente frecuente"
  }'

# Cita 3
curl -X POST http://127.0.0.1:8000/api/citas/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "stylist": 1,
    "service": 3,
    "fecha": "2024-02-22",
    "hora_inicio": "09:00:00",
    "hora_fin": "10:00:00",
    "estado": "pendiente",
    "observaciones": ""
  }'
```

### Actualizar una cita (confirmar)

```bash
curl -X PATCH http://127.0.0.1:8000/api/citas/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "confirmada"
  }'
```

### Cancelar una cita

```bash
curl -X PATCH http://127.0.0.1:8000/api/citas/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "cancelada"
  }'
```

### Marcar cita como completada

```bash
curl -X PATCH http://127.0.0.1:8000/api/citas/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "completada"
  }'
```

### Eliminar una cita

```bash
curl -X DELETE http://127.0.0.1:8000/api/citas/1/ \
  -H "Content-Type: application/json"
```

---

## ⏰ Horarios de Estilistas

### Listar todos los horarios

```bash
curl -X GET http://127.0.0.1:8000/api/horarios/ \
  -H "Content-Type: application/json"
```

### Obtener un horario específico

```bash
curl -X GET http://127.0.0.1:8000/api/horarios/1/ \
  -H "Content-Type: application/json"
```

### Crear horario - Lunes a Viernes

```bash
# Lunes
curl -X POST http://127.0.0.1:8000/api/horarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "stylist": 1,
    "dia_semana": "Lunes",
    "hora_inicio": "09:00:00",
    "hora_fin": "18:00:00",
    "activo": true
  }'

# Martes
curl -X POST http://127.0.0.1:8000/api/horarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "stylist": 1,
    "dia_semana": "Martes",
    "hora_inicio": "09:00:00",
    "hora_fin": "18:00:00",
    "activo": true
  }'

# Miércoles
curl -X POST http://127.0.0.1:8000/api/horarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "stylist": 1,
    "dia_semana": "Miercoles",
    "hora_inicio": "09:00:00",
    "hora_fin": "18:00:00",
    "activo": true
  }'

# Jueves
curl -X POST http://127.0.0.1:8000/api/horarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "stylist": 1,
    "dia_semana": "Jueves",
    "hora_inicio": "09:00:00",
    "hora_fin": "18:00:00",
    "activo": true
  }'

# Viernes
curl -X POST http://127.0.0.1:8000/api/horarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "stylist": 1,
    "dia_semana": "Viernes",
    "hora_inicio": "09:00:00",
    "hora_fin": "19:00:00",
    "activo": true
  }'

# Sábado (parcial)
curl -X POST http://127.0.0.1:8000/api/horarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "stylist": 1,
    "dia_semana": "Sabado",
    "hora_inicio": "10:00:00",
    "hora_fin": "16:00:00",
    "activo": true
  }'

# Domingo (cerrado)
curl -X POST http://127.0.0.1:8000/api/horarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "stylist": 1,
    "dia_semana": "Domingo",
    "hora_inicio": "00:00:00",
    "hora_fin": "00:00:00",
    "activo": false
  }'
```

### Actualizar un horario

```bash
curl -X PUT http://127.0.0.1:8000/api/horarios/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "stylist": 1,
    "dia_semana": "Lunes",
    "hora_inicio": "10:00:00",
    "hora_fin": "19:00:00",
    "activo": true
  }'
```

### Desactivar horario (cierre temporal)

```bash
curl -X PATCH http://127.0.0.1:8000/api/horarios/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "activo": false
  }'
```

### Eliminar un horario

```bash
curl -X DELETE http://127.0.0.1:8000/api/horarios/1/ \
  -H "Content-Type: application/json"
```

---

## 📊 Datos Anidados

### Obtener datos completos (estilistas con horarios y clientes con citas)

```bash
curl -X GET http://127.0.0.1:8000/api/data-anidada/ \
  -H "Content-Type: application/json"
```

**Respuesta exitosa (200 OK)**:
```json
[
  {
    "usuario_id": 3,
    "nombre_completo": "Sofia Mendez",
    "correo_electronico": "sofia-mendez@bellaestetica.com",
    "telefono": "555-4444444",
    "rol": "estilista",
    "estado_cuenta": "active",
    "perfil_estilista": {
      "especialidad": "Cortes y Peinados",
      "peluquereria_asignada": {
        "nombre_comercial": "Bella Estética Centro",
        "telefono_contacto": "555-1234567",
        "direccion_fisica": "Calle Principal 123, Piso 2",
        "descripcion": "Peluquería de lujo en el centro de la ciudad"
      },
      "horarios_atencion": [
        {
          "dia_semana": "Lunes",
          "hora_inicio": "09:00:00",
          "hora_fin": "18:00:00",
          "activo": true
        }
      ]
    }
  },
  {
    "usuario_id": 1,
    "nombre_completo": "Juan Pérez García",
    "correo_electronico": "juan.perez@gmail.com",
    "telefono": "555-1111111",
    "rol": "cliente",
    "estado_cuenta": "active",
    "historial_citas": [
      {
        "fecha_reserva": "2024-02-20",
        "hora_inicio": "10:00:00",
        "hora_fin": "10:45:00",
        "estado_cita": "confirmada",
        "lugar_cita": {
          "nombre_comercial": "Bella Estética Centro",
          "direccion_fisica": "Calle Principal 123, Piso 2"
        },
        "servicio_solicitado": {
          "nombre_servicio": "Corte de Cabello",
          "descripcion": "Corte profesional con técnicas modernas",
          "costo": 35.0,
          "duracion_minutos": 45
        },
        "profesional_asignado": {
          "nombre": "Sofia Mendez",
          "especialidad": "Cortes y Peinados"
        }
      }
    ]
  }
]
```

---

## 🔍 Scripts de Prueba Rápida

### Script para crear datos de prueba completos

```bash
#!/bin/bash

# Base URL
BASE_URL="http://127.0.0.1:8000/api"

echo "1. Creando Peluquerías..."
PELUQUERIA=$(curl -s -X POST $BASE_URL/peluquerias/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bella Estética",
    "direccion": "Calle Central 123",
    "telefono": "555-0000000",
    "descripcion": "Salón de belleza premium"
  }' | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

echo "✓ Peluquería creada: ID=$PELUQUERIA"

echo "2. Creando Usuarios..."
USUARIO=$(curl -s -X POST $BASE_URL/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Cliente Test",
    "email": "cliente@test.com",
    "password": "test123",
    "telefono": "555-1234567",
    "rol": "cliente"
  }' | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

echo "✓ Usuario creado: ID=$USUARIO"

echo "3. Creando Estilistas..."
ESTILISTA=$(curl -s -X POST $BASE_URL/estilistas/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Estilista Test",
    "especialidad": "Cortes",
    "telefono": "555-7654321",
    "hair_salon": '$PELUQUERIA'
  }' | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

echo "✓ Estilista creado: ID=$ESTILISTA"

echo "4. Creando Servicios..."
SERVICIO=$(curl -s -X POST $BASE_URL/servicios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Corte Básico",
    "descripcion": "Corte estándar",
    "precio": "30.00",
    "duracion_minutos": 30,
    "hair_salon": '$PELUQUERIA'
  }' | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

echo "✓ Servicio creado: ID=$SERVICIO"

echo "5. Creando Cita..."
CITA=$(curl -s -X POST $BASE_URL/citas/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": '$USUARIO',
    "stylist": '$ESTILISTA',
    "service": '$SERVICIO',
    "fecha": "2024-02-25",
    "hora_inicio": "14:00:00",
    "hora_fin": "14:30:00"
  }' | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

echo "✓ Cita creada: ID=$CITA"

echo ""
echo "✅ Datos de prueba creados exitosamente!"
echo "IDs creados:"
echo "  - Peluquería: $PELUQUERIA"
echo "  - Usuario: $USUARIO"
echo "  - Estilista: $ESTILISTA"
echo "  - Servicio: $SERVICIO"
echo "  - Cita: $CITA"
```

---

## ⚙️ Headers Opcionales

Si en producción implementas autenticación JWT, incluye este header:

```bash
curl -X GET http://127.0.0.1:8000/api/peluquerias/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tu_token_jwt_aqui"
```

Para obtener el token (una vez restaurada la autenticación):

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "123"
  }'
```

---

## ✅ Códigos de Respuesta HTTP

| Código | Significado |
|--------|------------|
| `200 OK` | Solicitud exitosa |
| `201 Created` | Recurso creado exitosamente |
| `204 No Content` | Recurso eliminado exitosamente |
| `400 Bad Request` | Datos inválidos |
| `401 Unauthorized` | Autenticación requerida (producción) |
| `404 Not Found` | Recurso no encontrado |
| `500 Server Error` | Error del servidor |

---

## 🧪 Herramientas Recomendadas para Probar

### Postman
- Descarga: https://www.postman.com/downloads/
- Importa estos endpoints en una colección
- Ideal para documentar y compartir

### Thunder Client (VS Code)
- Extensión para VS Code
- Más ligera que Postman

### curl (CLI)
- Ya incluido en sistemas Unix/Linux/macOS
- Windows 10+ también lo incluye

### REST Client (VS Code)
- Extensión: `REST Client` (Huachao Mao)
- Prueba directamente en VS Code

---

## 📝 Notas Importantes

1. **Validaciones de Teléfono**: Mínimo 7 dígitos
2. **Duración de Servicios**: Debe coincidir con la duración de la cita
3. **Validación de Horarios**: El estilista y servicio deben estar en la misma peluquería
4. **Sin Conflictos**: No se pueden crear dos citas para el mismo estilista en horarios superpuestos
5. **Estados de Cita**: `pendiente`, `confirmada`, `completada`, `cancelada`
6. **Roles de Usuario**: `cliente`, `administrador`, `recepcionista`

---

**Última actualización**: 2024-02-18
**Versión de API**: 1.0
**Versión de Django**: 6.0.4
**Versión de Django REST Framework**: 3.17.1

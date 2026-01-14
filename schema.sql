-- Estructura de la base de datos:

-- 1. Tabla Maestra: Información fija del producto
CREATE TABLE IF NOT EXISTS Productos_Vigilados (
    id_producto SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    url_amazon TEXT UNIQUE NOT NULL, -- UNIQUE evita que registres el mismo link dos veces
    imagen_url TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla Historial: Registra los cambios de precio en el tiempo
CREATE TABLE IF NOT EXISTS Info_Product (
    id_historial SERIAL PRIMARY KEY,
    id_producto INTEGER REFERENCES Productos_Vigilados(id_producto) ON DELETE CASCADE,
    precio DECIMAL(10, 2) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
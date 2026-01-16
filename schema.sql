-- Estructura de la base de datos:

-- Tabla Maestra: Guarda los productos únicos (para no repetir nombres/fotos)
CREATE TABLE IF NOT EXISTS Productos_Vigilados (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    url_amazon TEXT UNIQUE, -- UNIQUE es clave para el ON CONFLICT de tu código
    imagen_url TEXT
);

-- Tabla Historial: Guarda los precios cada vez que buscas
CREATE TABLE IF NOT EXISTS Info_Product (
    id_registro SERIAL PRIMARY KEY,
    id_producto INT REFERENCES Productos_Vigilados(id_producto),
    precio NUMERIC(10, 2), -- NUMERIC es mejor que FLOAT para dinero
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

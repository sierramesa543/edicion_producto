-- Script opcional: crea la tabla "productos" con datos de ejemplo.
-- Ejecútalo en tu base de datos PostgreSQL SOLO si aún no la tienes.

CREATE TABLE IF NOT EXISTS productos (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100)  NOT NULL,
    precio      NUMERIC(10,2) NOT NULL CHECK (precio > 0),
    cantidad    INTEGER       NOT NULL CHECK (cantidad >= 0),
    descripcion TEXT
);

INSERT INTO productos (nombre, precio, cantidad, descripcion) VALUES
    ('Cuaderno rayado',   4500.00, 120, 'Cuaderno de 100 hojas'),
    ('Lápiz HB',           800.00, 500, NULL),
    ('Borrador',           600.00, 300, 'Borrador blanco grande'),
    ('Regla de 30 cm',    2500.00,  80, 'Plástico transparente');

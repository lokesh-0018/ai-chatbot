"""
Database Module for AI Laptop Selection Chatbot Expert System
Handles SQLite database connection, table initialization, and sample laptop records.
"""

import sqlite3
import os

# Default database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DEFAULT_DB_PATH = os.path.join(DB_DIR, "laptops.db")

SAMPLE_LAPTOPS = [
    {
        "name": "Lenovo IdeaPad Slim 3",
        "brand": "Lenovo",
        "price": 38990,
        "processor": "Intel Core i3 12th Gen",
        "cpu_score": 62,
        "ram": 8,
        "storage": 512,
        "gpu": "Integrated Intel UHD",
        "gpu_score": 30,
        "display": 15.6,
        "refresh_rate": 60,
        "battery": 7.0,
        "weight": 1.63,
        "primary_usage": "Student / General Use",
        "description": "Affordable daily driver with anti-glare screen and reliable battery for basic computing."
    },
    {
        "name": "HP 15s-fq5007TU",
        "brand": "HP",
        "price": 44990,
        "processor": "Intel Core i5 12th Gen",
        "cpu_score": 74,
        "ram": 8,
        "storage": 512,
        "gpu": "Integrated Intel Iris Xe",
        "gpu_score": 42,
        "display": 15.6,
        "refresh_rate": 60,
        "battery": 7.5,
        "weight": 1.69,
        "primary_usage": "Office Work",
        "description": "Clean modern design with micro-edge bezel and fast charging for office and academic work."
    },
    {
        "name": "Dell Inspiron 14 5430",
        "brand": "Dell",
        "price": 49990,
        "processor": "Intel Core i5 12th Gen",
        "cpu_score": 76,
        "ram": 16,
        "storage": 512,
        "gpu": "Integrated Intel Iris Xe",
        "gpu_score": 42,
        "display": 14.0,
        "refresh_rate": 60,
        "battery": 8.0,
        "weight": 1.54,
        "primary_usage": "Student / Programming",
        "description": "Compact 14-inch productivity notebook with 16GB RAM for multitasking and software development."
    },
    {
        "name": "ASUS Vivobook 16X",
        "brand": "ASUS",
        "price": 52990,
        "processor": "AMD Ryzen 5 5600H",
        "cpu_score": 80,
        "ram": 16,
        "storage": 512,
        "gpu": "Integrated AMD Radeon",
        "gpu_score": 45,
        "display": 16.0,
        "refresh_rate": 60,
        "battery": 6.5,
        "weight": 1.80,
        "primary_usage": "Programming",
        "description": "Spacious 16-inch workspace with an H-series high performance processor ideal for coding."
    },
    {
        "name": "Acer Swift Go 14 OLED",
        "brand": "Acer",
        "price": 59990,
        "processor": "Intel Core i5 13th Gen",
        "cpu_score": 84,
        "ram": 16,
        "storage": 512,
        "gpu": "Integrated Intel Iris Xe",
        "gpu_score": 45,
        "display": 14.0,
        "refresh_rate": 90,
        "battery": 9.5,
        "weight": 1.25,
        "primary_usage": "Student / Portability",
        "description": "Ultra-lightweight metal chassis with breathtaking 2.8K 90Hz OLED display and all-day battery."
    },
    {
        "name": "Lenovo ThinkPad E14 Gen 5",
        "brand": "Lenovo",
        "price": 62490,
        "processor": "AMD Ryzen 5 7530U",
        "cpu_score": 81,
        "ram": 16,
        "storage": 512,
        "gpu": "Integrated AMD Radeon",
        "gpu_score": 46,
        "display": 14.0,
        "refresh_rate": 60,
        "battery": 9.0,
        "weight": 1.41,
        "primary_usage": "Programming",
        "description": "Legendary ThinkPad keyboard ergonomics, military-grade durability, and robust Linux compatibility."
    },
    {
        "name": "Lenovo LOQ 15",
        "brand": "Lenovo",
        "price": 64990,
        "processor": "Intel Core i5 12th Gen",
        "cpu_score": 82,
        "ram": 16,
        "storage": 512,
        "gpu": "NVIDIA RTX 3050",
        "gpu_score": 72,
        "display": 15.6,
        "refresh_rate": 144,
        "battery": 5.5,
        "weight": 2.38,
        "primary_usage": "Gaming",
        "description": "Budget gaming champion with RTX 3050 dedicated GPU, 144Hz high-refresh display, and dual cooling fans."
    },
    {
        "name": "ASUS TUF Gaming A15",
        "brand": "ASUS",
        "price": 69999,
        "processor": "AMD Ryzen 7 7735HS",
        "cpu_score": 88,
        "ram": 16,
        "storage": 512,
        "gpu": "NVIDIA RTX 4050",
        "gpu_score": 84,
        "display": 15.6,
        "refresh_rate": 144,
        "battery": 6.5,
        "weight": 2.20,
        "primary_usage": "Gaming / Programming",
        "description": "High performance 8-core Ryzen 7 paired with Next-Gen Ada Lovelace RTX 4050 for heavy workloads."
    },
    {
        "name": "Acer Nitro V 15",
        "brand": "Acer",
        "price": 72990,
        "processor": "Intel Core i5 13th Gen",
        "cpu_score": 85,
        "ram": 16,
        "storage": 512,
        "gpu": "NVIDIA RTX 4050",
        "gpu_score": 84,
        "display": 15.6,
        "refresh_rate": 144,
        "battery": 5.0,
        "weight": 2.10,
        "primary_usage": "Gaming / Video Editing",
        "description": "13th Gen Intel hybrid architecture coupled with RTX 4050 GPU for seamless 1080p video editing and gaming."
    },
    {
        "name": "HP Victus 16",
        "brand": "HP",
        "price": 77990,
        "processor": "AMD Ryzen 7 7840HS",
        "cpu_score": 90,
        "ram": 16,
        "storage": 1024,
        "gpu": "NVIDIA RTX 4050",
        "gpu_score": 84,
        "display": 16.1,
        "refresh_rate": 144,
        "battery": 6.0,
        "weight": 2.30,
        "primary_usage": "Gaming / AI / Machine Learning",
        "description": "Zen 4 processor with dedicated AI NPU, generous 1TB NVMe SSD storage, and smooth 16.1-inch IPS panel."
    },
    {
        "name": "ASUS Zenbook 14 OLED",
        "brand": "ASUS",
        "price": 79990,
        "processor": "Intel Core Ultra 5",
        "cpu_score": 87,
        "ram": 16,
        "storage": 1024,
        "gpu": "Integrated Intel Arc",
        "gpu_score": 60,
        "display": 14.0,
        "refresh_rate": 120,
        "battery": 12.0,
        "weight": 1.28,
        "primary_usage": "Programming / Portability",
        "description": "Premium ultraportable with Intel Meteor Lake AI boost, vivid 3K 120Hz OLED screen, and 12-hour endurance."
    },
    {
        "name": "HP Envy x360 2-in-1",
        "brand": "HP",
        "price": 81990,
        "processor": "AMD Ryzen 7 7730U",
        "cpu_score": 83,
        "ram": 16,
        "storage": 512,
        "gpu": "Integrated AMD Radeon",
        "gpu_score": 48,
        "display": 15.6,
        "refresh_rate": 60,
        "battery": 10.0,
        "weight": 1.82,
        "primary_usage": "Graphic Design",
        "description": "Versatile convertible touchscreen with pen support, calibrated color accuracy, and premium aluminum finish."
    },
    {
        "name": "Dell G15 5530",
        "brand": "Dell",
        "price": 82490,
        "processor": "Intel Core i7 13th Gen",
        "cpu_score": 91,
        "ram": 16,
        "storage": 1024,
        "gpu": "NVIDIA RTX 3050",
        "gpu_score": 76,
        "display": 15.6,
        "refresh_rate": 120,
        "battery": 5.5,
        "weight": 2.65,
        "primary_usage": "Programming / Gaming",
        "description": "Alienware-inspired thermal cooling with high thread-count Core i7 for intense simulation and compile jobs."
    },
    {
        "name": "Apple MacBook Air M2",
        "brand": "Apple",
        "price": 84900,
        "processor": "Apple M2 8-Core",
        "cpu_score": 89,
        "ram": 16,
        "storage": 512,
        "gpu": "Apple M2 10-Core GPU",
        "gpu_score": 70,
        "display": 13.6,
        "refresh_rate": 60,
        "battery": 18.0,
        "weight": 1.24,
        "primary_usage": "Student / Programming",
        "description": "Unmatched battery efficiency (up to 18 hours), silent fanless chassis, Liquid Retina display, and UNIX macOS."
    },
    {
        "name": "Lenovo Legion Slim 5",
        "brand": "Lenovo",
        "price": 94990,
        "processor": "AMD Ryzen 7 7840HS",
        "cpu_score": 92,
        "ram": 16,
        "storage": 1024,
        "gpu": "NVIDIA RTX 4060",
        "gpu_score": 92,
        "display": 16.0,
        "refresh_rate": 165,
        "battery": 7.0,
        "weight": 2.30,
        "primary_usage": "Gaming / AI / Machine Learning",
        "description": "Powerhouse RTX 4060 with 8GB VRAM, 165Hz WQXGA panel, AI Engine+ tuning, and full-size TrueStrike keyboard."
    },
    {
        "name": "MSI Creator M16",
        "brand": "MSI",
        "price": 104990,
        "processor": "Intel Core i7 13th Gen",
        "cpu_score": 93,
        "ram": 32,
        "storage": 1024,
        "gpu": "NVIDIA RTX 4060",
        "gpu_score": 92,
        "display": 16.0,
        "refresh_rate": 60,
        "battery": 6.0,
        "weight": 2.26,
        "primary_usage": "Video Editing / Graphic Design",
        "description": "Purpose-built for digital content creators with factory-calibrated 100% DCI-P3 display and 32GB high-speed memory."
    },
    {
        "name": "ASUS ROG Strix G16",
        "brand": "ASUS",
        "price": 118990,
        "processor": "Intel Core i7 13650HX",
        "cpu_score": 95,
        "ram": 16,
        "storage": 1024,
        "gpu": "NVIDIA RTX 4060",
        "gpu_score": 92,
        "display": 16.0,
        "refresh_rate": 165,
        "battery": 6.5,
        "weight": 2.50,
        "primary_usage": "Gaming / AI / Machine Learning",
        "description": "Desktop-grade HX processor, Conductonaut Extreme liquid metal cooling, ROG Nebula Display, and MUX Switch."
    },
    {
        "name": "Acer Predator Helios Neo 16",
        "brand": "Acer",
        "price": 134990,
        "processor": "Intel Core i9 14th Gen",
        "cpu_score": 98,
        "ram": 32,
        "storage": 1024,
        "gpu": "NVIDIA RTX 4070",
        "gpu_score": 97,
        "display": 16.0,
        "refresh_rate": 240,
        "battery": 5.5,
        "weight": 2.60,
        "primary_usage": "AI / Machine Learning",
        "description": "Top-tier flagship equipped with 24-core i9 14900HX, RTX 4070 8GB VRAM, 32GB RAM, and 240Hz lightning panel."
    }
]


def init_db(db_path=None):
    """Initializes the SQLite database and populates with sample data if empty."""
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create laptops table with complete schema matching prompt requirements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS laptops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            price INTEGER NOT NULL,
            processor TEXT NOT NULL,
            cpu_score INTEGER NOT NULL,
            ram INTEGER NOT NULL,
            storage INTEGER NOT NULL,
            gpu TEXT NOT NULL,
            gpu_score INTEGER NOT NULL,
            display REAL NOT NULL,
            refresh_rate INTEGER NOT NULL,
            battery REAL NOT NULL,
            weight REAL NOT NULL,
            primary_usage TEXT NOT NULL,
            description TEXT
        )
    """)

    # Check if table already contains data
    cursor.execute("SELECT COUNT(*) FROM laptops")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO laptops (
                name, brand, price, processor, cpu_score, ram, storage,
                gpu, gpu_score, display, refresh_rate, battery, weight,
                primary_usage, description
            ) VALUES (
                :name, :brand, :price, :processor, :cpu_score, :ram, :storage,
                :gpu, :gpu_score, :display, :refresh_rate, :battery, :weight,
                :primary_usage, :description
            )
        """, SAMPLE_LAPTOPS)
        conn.commit()

    conn.close()


def get_db_connection(db_path=None):
    """Returns a SQLite connection with Row factory enabled."""
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    if not os.path.exists(db_path):
        init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_laptops(db_path=None):
    """Fetches all laptop records as a list of dictionaries."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM laptops ORDER BY price ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_laptop_by_id(laptop_id, db_path=None):
    """Fetches a single laptop record by ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM laptops WHERE id = ?", (laptop_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


if __name__ == "__main__":
    init_db()
    laptops = get_all_laptops()
    print(f"Database initialized successfully with {len(laptops)} laptops.")

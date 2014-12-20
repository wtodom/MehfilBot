CREATE TABLE menu (
  menu_id SERIAL PRIMARY KEY,
  date VARCHAR(40) NOT NULL,
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE menu_item (
  menu_item_id SERIAL PRIMARY KEY,
  menu_id INT NOT NULL REFERENCES menu (menu_id),
  item_number SMALLINT NOT NULL,
  name VARCHAR(50) NOT NULL,
  description VARCHAR(200) NOT NULL,
  price NUMERIC(4,2) NOT NULL
);

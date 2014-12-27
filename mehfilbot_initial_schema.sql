CREATE TABLE mehfilbot.menu (
  menu_id SERIAL PRIMARY KEY,
  menu_date DATE NOT NULL,
  has_been_tweeted SMALLINT NOT NULL DEFAULT 0,
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mehfilbot.menu_item (
  menu_item_id SERIAL PRIMARY KEY,
  menu_id INT NOT NULL REFERENCES mehfilbot.menu (menu_id),
  item_number SMALLINT NOT NULL,
  name VARCHAR(50) NOT NULL,
  description VARCHAR(200) NOT NULL,
  price NUMERIC(4,2) NOT NULL
);

ALTER TABLE mehfilbot.menu ADD CONSTRAINT menu_date_UNIQUE UNIQUE (menu_date);

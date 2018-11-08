CREATE TABLE Groups(group_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
group_fb_id VARCHAR(255), 
group_name VARCHAR(255),
update_date DATE);

CREATE INDEX g_index ON Groups (group_name);


CREATE TABLE Cities(city_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
city_name VARCHAR(255));

CREATE INDEX c_index ON Cities (city_name);


CREATE TABLE States(state_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
state_name VARCHAR(255));

CREATE INDEX s_index ON States (state_name);


CREATE TABLE Companies(company_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
company_name VARCHAR(255));

CREATE INDEX c_index ON Companies (company_name);


CREATE TABLE CitiesStates(city_id INT NOT NULL,
state_id INT NOT NULL,
PRIMARY KEY(city_id, state_id));


CREATE TABLE JobPost(post_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
post_story_id TEXT, 
publish_date DATE,
employment_form INT(1) NOT NULL DEFAULT 0,
working_manner BOOL NOT NULL DEFAULT FALSE,
email VARCHAR(254),
full_post_body TEXT);

ALTER TABLE JobPost ENGINE = MyISAM;

CREATE FULLTEXT INDEX p_index ON JobPost(full_post_body);


CREATE TABLE JobPostGroup(post_id INT NOT NULL, 
group_id INT NOT NULL,
PRIMARY KEY(post_id, group_id));



CREATE TABLE JobPostCity(post_id INT NOT NULL, 
city_id INT NOT NULL,
PRIMARY KEY(post_id, city_id));



CREATE TABLE JobPostCompany(post_id INT NOT NULL, 
company_id INT NOT NULL,
PRIMARY KEY(post_id, company_id));


CREATE TABLE JobPostState(post_id INT NOT NULL, 
state_id VARCHAR(2) NOT NULL,
PRIMARY KEY(post_id, state_id));

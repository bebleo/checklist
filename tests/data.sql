/* Data to be inserted into the database for test purposes
 *
 *  */

INSERT INTO users (email, password) 
VALUES
  ('test@bebleo.url', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other@bebleo.url', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO checklists (title, [description], created_by, assigned_to)
VALUES 
  ('List no. 1', 'A list inserted for testing purposes', 1, 1),
  ('List no. 2', '', 2, 2);

INSERT INTO checklist_items (item_text, done, checklist_id) 
VALUES 
  ('Item 1.1', False, 1),
  ('Item 1.2', False, 1),
  ('Item 1.3', False, 1),
  ('Item 2.1', True, 2),
  ('Item 2.2', True, 2),
  ('Item 2.3', False, 2);

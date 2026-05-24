import unittest
import os
import json

class TestMovieScraperOutputs(unittest.TestCase):
    
    def test_csv_file_exists_and_not_empty(self):
        """Verifica se o arquivo CSV foi criado e contém dados"""
        self.assertTrue(os.path.exists("movies.csv"), "O arquivo movies.csv não foi criado.")
        size = os.path.getsize("movies.csv")
        self.assertGreater(size, 50, "O arquivo CSV está vazio ou contém apenas o cabeçalho.")

    def test_json_file_exists_and_is_valid(self):
        """Verifica se o arquivo JSON existe e possui a estrutura correta"""
        self.assertTrue(os.path.exists("movies.json"), "O arquivo movies.json não foi criado.")
        
        with open("movies.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertIsInstance(data, list, "O JSON deveria ser uma lista de objetos.")
        if len(data) > 0:
            primeiro_filme = data[0]
            self.assertIn("nome", primeiro_filme)
            self.assertIn("data_lancamento", primeiro_filme)
            self.assertIn("nota", primeiro_filme)
            self.assertIn("sinopse", primeiro_filme)

if __name__ == "__main__":
    unittest.main()
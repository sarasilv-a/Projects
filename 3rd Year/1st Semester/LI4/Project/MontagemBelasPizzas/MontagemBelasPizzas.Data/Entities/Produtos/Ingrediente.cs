namespace MontagemBelasPizzas.Data.Entities.Produtos
{
    public class Ingrediente
    {
        public int Id { get; set; } // Chave primária
        public string Nome { get; set; } // Nome do ingrediente
        public decimal Preco { get; set; } // Preço do ingrediente
        public int QuantidadeEmStock { get; set; } // Quantidade em stock
        public bool EmUso { get; set; } // Se está ou não em uso
        public string ImagemURL { get; set; } // URL da imagem do ingrediente
        public int IdAdministrador { get; set; } // FK para o administrador
    }
}

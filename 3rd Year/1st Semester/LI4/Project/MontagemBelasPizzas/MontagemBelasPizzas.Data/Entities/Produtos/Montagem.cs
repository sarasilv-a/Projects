namespace MontagemBelasPizzas.Data.Entities.Produtos
{
    public class Montagem
    {
        public int Id { get; set; } // Chave pngrediente
        public int IdProduto { get; set; } // FK para Produtrimária
        public int IdIngrediente { get; set; } // FK para Io
        public int Ordem { get; set; } // Ordem da montagem
        public string Descricao { get; set; } // Descrição do passo da montagem
        
        public override string ToString()
        {
            return $"Montagem: Id={Id}, IdIngrediente={IdIngrediente}, IdProduto={IdProduto}, Ordem={Ordem}, Descricao='{Descricao}'";
        }
    }
}

namespace MontagemBelasPizzas.Data.Entities.Produtos
{
    public class Venda : Operacao
    {
        public int IdProduto { get; set; } // FK para Produto
    }
}

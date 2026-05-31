namespace MontagemBelasPizzas.Data.Entities.Produtos
{
    public class Compra : Operacao
    {
        public int IdIngrediente { get; set; } // FK para Ingrediente
    }
}

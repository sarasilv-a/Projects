namespace MontagemBelasPizzas.Data.Entities.Produtos
{
    public class LinhaDeMontagem
    {
        public int Id { get; set; } // Chave primária
        public DateTime DataDeInicio { get; set; } // Data de início da linha de montagem
        public DateTime? DataDeFim { get; set; } // Data de fim (opcional)
        public bool Estado { get; set; } // Estado (ativo/inativo)
        public int Satisfacao { get; set; } // Satisfação do Funcionário
        public int IdFuncionario { get; set; } // FK para Funcionário
        public int IdProduto { get; set; } // FK para Produto
    }
}

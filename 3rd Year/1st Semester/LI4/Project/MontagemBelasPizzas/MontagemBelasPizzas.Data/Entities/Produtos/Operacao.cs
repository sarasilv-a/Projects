namespace MontagemBelasPizzas.Data.Entities.Produtos
{
    public class Operacao
    {
        public int Id { get; set; } // Chave primária
        public int Quantidade { get; set; } // Quantidade
        public decimal ValorUnitario { get; set; } // Valor unitário
        public decimal ValorTotal { get; set; } // Valor total
        public DateTime DataDaOperacao { get; set; } // Data da operação
        public int IdAdministrador { get; set; } // FK para Administrador
    }
}

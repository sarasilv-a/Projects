namespace MontagemBelasPizzas.Data.Entities.Utilizadores
{
    public class Utilizador
    {
        public int Id { get; set; } // Número inteiro positivo
        public string Nome { get; set; } // Nome do utilizador
        public string Senha { get; set; } // Hash da senha do utilizador
        public string NIF { get; set; } // Número único de 9 dígitos
        public DateTime? DataDeNascimento { get; set; } // Data de nascimento
        public DateTime DataDeCriacao { get; set; } // Data de criação do registo
        public string? ImagemURL { get; set; } // Caminho ou URL da imagem (opcional)
        public int QuantidadeDeProdutosRealizados { get; set; } // Número inteiro não negativo
        public int QuantidadeDeProdutosRejeitados { get; set; } // Número inteiro não negativo
        public decimal MediaDeSatisfacao { get; set; } // Valor decimal entre 1.0 e 5.0
        public TimeSpan TempoMedioPorProduto { get; set; } // Tempo médio (HH:MM:SS)
        public TipoUtilizador Tipo { get; set; } // Administrador ou Funcionário
    }

    public enum TipoUtilizador
    {
        Administrador,
        Funcionario
    }
}

namespace MontagemBelasPizzas.Data.Entities.Produtos;

public class Produto
{
    public int Id { get; set; } // Chave primária
    public string Nome { get; set; } // Nome do produto
    public string Categoria { get; set; } // Categoria do produto
    public decimal Preco { get; set; } // Preço do produto
    public int QuantidadeDeRealizacoes { get; set; } // Total de realizações
    public int QuantidadeDeVendas { get; set; } // Total de vendas
    public int QuantidadeDeRejeicoes { get; set; } // Total de rejeições
    public decimal MediaDeSatisfacao { get; set; } // Média de satisfação (1.0 a 5.0)
    public TimeSpan MediaDoTempoDeMontagem { get; set; } // Tempo médio de montagem
    public int QuantidadeEmStock { get; set; } // Quantidade em stock
    public string ImagemURL { get; set; } // URL da imagem do produto
    public int IdAdministrador { get; set; } // FK para o administrador
}


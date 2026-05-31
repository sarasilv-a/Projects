using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Repositories.Produtos;

namespace MontagemBelasPizzas.Business.Services.Produtos
{
    public class OperacaoService
    {
        private readonly OperacaoRepository _operacaoRepository;

        public OperacaoService(OperacaoRepository operacaoRepository)
        {
            _operacaoRepository = operacaoRepository;
        }

        // Obter todas as compras
        public async Task<IEnumerable<Compra>> GetAllCompras()
        {
            return await _operacaoRepository.GetAllCompras();
        }

        // Obter todas as compras por administrador
        public async Task<IEnumerable<Compra>> GetAllComprasByAdminId(int adminId)
        {
            return await _operacaoRepository.GetAllComprasByAdminId(adminId);
        }

        // Obter todas as vendas
        public async Task<IEnumerable<Venda>> GetAllVendas()
        {
            return await _operacaoRepository.GetAllVendas();
        }

        // Obter todas as vendas por administrador
        public async Task<IEnumerable<Venda>> GetAllVendasByAdminId(int adminId)
        {
            return await _operacaoRepository.GetAllVendasByAdminId(adminId);
        }

        public async Task AddCompra(int idIngrediente, int quantidade, int idAdministrador, decimal preco)
        {
            var valorUnitario = preco;
            var valorTotal = valorUnitario * quantidade;

            var parameters = new
            {
                IdIngrediente = idIngrediente,
                Quantidade = quantidade,
                ValorUnitario = valorUnitario,
                ValorTotal = valorTotal,
                IdAdministrador = idAdministrador
            };

            await _operacaoRepository.AddCompra(parameters);
        }

        public async Task AddVenda(int idProduto, int quantidade, int idAdministrador, decimal preco, int qtProduto)
        {
            // Verificar se a quantidade em stock é suficiente
            if (qtProduto < quantidade)
            {
                throw new Exception($"Stock insuficiente para o produto '{idProduto}'. Stock atual: {qtProduto}, Pedido: {quantidade}");
            }

            var valorUnitario = preco;
            var valorTotal = valorUnitario * quantidade;

            var parameters = new
            {
                IdProduto = idProduto,
                Quantidade = quantidade,
                ValorUnitario = valorUnitario,
                ValorTotal = valorTotal,
                IdAdministrador = idAdministrador
            };

            await _operacaoRepository.AddVenda(parameters);
        }

        public async Task<List<int>> GetSalesPerMonth()
        {
            return await _operacaoRepository.GetSalesPerMonth();
        }

        // Obter compras por mês
        public async Task<List<int>> GetBuysPerMonth()
        {
            return await _operacaoRepository.GetBuysPerMonth();
        }
        
        public async Task<IEnumerable<(Produto Produto, int QuantidadeVendida)>> GetTop5MostSoldProducts()
        {
            return await _operacaoRepository.GetTop5MostSoldProducts();
        }
    }
}


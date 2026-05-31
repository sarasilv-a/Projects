using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Interfaces;

namespace MontagemBelasPizzas.Data.Repositories.Produtos
{
    public class ProdutoRepository
    {
        private readonly ISqlDataAccess _db;

        public ProdutoRepository(ISqlDataAccess db)
        {
            _db = db;
        }

        public async Task<Produto?> GetById(int id)
        {
            var parameters = new { Id = id };
            var result = await _db.LoadData<Produto, dynamic>(
                storedProcedure: "spProduto_GetById",
                parameters: parameters
            );

            return result.FirstOrDefault();
        }

        public async Task<IEnumerable<Produto>> GetAll()
        {
            var result = await _db.LoadData<Produto, dynamic>(
                storedProcedure: "spProduto_GetAll",
                parameters: new { }
            );

            return result;
        }

        public async Task<IEnumerable<Produto>> GetTop3MaisVendidos()
        {
            var result = await _db.LoadData<Produto, dynamic>(
                storedProcedure: "spProduto_GetTop3MaisVendidos",
                parameters: new { }
            );

            return result;
        }

        public async Task Insert(Produto produto)
        {
            var parameters = new
            {
                produto.Nome,
                produto.Categoria,
                produto.Preco,
                produto.QuantidadeDeRealizacoes,
                produto.QuantidadeDeVendas,
                produto.QuantidadeDeRejeicoes,
                produto.MediaDeSatisfacao,
                produto.MediaDoTempoDeMontagem,
                produto.QuantidadeEmStock,
                produto.ImagemURL,
                produto.IdAdministrador
            };

            await _db.SaveData("spProduto_Insert", parameters);
        }

        public async Task Update(Produto produto)
        {
            var parameters = new
            {
                produto.Id,
                produto.Nome,
                produto.Categoria,
                produto.Preco,
                produto.QuantidadeDeRealizacoes,
                produto.QuantidadeDeVendas,
                produto.QuantidadeDeRejeicoes,
                produto.MediaDeSatisfacao,
                produto.MediaDoTempoDeMontagem,
                produto.QuantidadeEmStock,
                produto.ImagemURL,
                produto.IdAdministrador
            };

            await _db.SaveData("spProduto_Update", parameters);
        }

        public async Task Delete(int id)
        {
            var parameters = new { Id = id };
            await _db.SaveData("spProduto_Delete", parameters);
        }
    }
}


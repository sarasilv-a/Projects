using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Interfaces;

namespace MontagemBelasPizzas.Data.Repositories.Produtos
{
    public class MontagemRepository
    {
        private readonly ISqlDataAccess _db;

        public MontagemRepository(ISqlDataAccess db)
        {
            _db = db;
        }

        public async Task<Montagem?> GetById(int id)
        {
            var parameters = new { Id = id };
            var result = await _db.LoadData<Montagem, dynamic>(
                storedProcedure: "spMontagem_GetById",
                parameters: parameters
            );

            return result.FirstOrDefault();
        }

        public async Task<IEnumerable<Montagem>> GetAll()
        {
            var result = await _db.LoadData<Montagem, dynamic>(
                storedProcedure: "spMontagem_GetAll",
                parameters: new { }
            );

            return result;
        }

        public async Task<IEnumerable<Montagem>> GetByProdutoId(int produtoId)
        {
            var parameters = new { IdProduto = produtoId };
            return await _db.LoadData<Montagem, dynamic>(
                storedProcedure: "spMontagem_GetByProdutoId",
                parameters: parameters
            );
        }

        public async Task Insert(Montagem montagem)
        {
            var parameters = new
            {
                montagem.IdIngrediente,
                montagem.IdProduto,
                montagem.Ordem,
                montagem.Descricao
            };

            await _db.SaveData("spMontagem_Insert", parameters);
        }

        public async Task Update(Montagem montagem)
        {
            var parameters = new
            {
                montagem.Id,
                montagem.IdIngrediente,
                montagem.IdProduto,
                montagem.Ordem,
                montagem.Descricao
            };

            await _db.SaveData("spMontagem_Update", parameters);
        }

        public async Task Delete(int id)
        {
            var parameters = new { Id = id };
            await _db.SaveData("spMontagem_Delete", parameters);
        }
    }
}

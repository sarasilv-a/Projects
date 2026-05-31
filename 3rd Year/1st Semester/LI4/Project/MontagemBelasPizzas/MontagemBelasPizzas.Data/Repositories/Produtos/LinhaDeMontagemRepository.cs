using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Interfaces;

namespace MontagemBelasPizzas.Data.Repositories.Produtos
{
    public class LinhaDeMontagemRepository
    {
        private readonly ISqlDataAccess _db;

        public LinhaDeMontagemRepository(ISqlDataAccess db)
        {
            _db = db;
        }

        public async Task<LinhaDeMontagem?> GetById(int id)
        {
            var parameters = new { Id = id };
            var result = await _db.LoadData<LinhaDeMontagem, dynamic>(
                storedProcedure: "spLinhaDeMontagem_GetById",
                parameters: parameters
            );

            return result.FirstOrDefault();
        }

        public async Task<IEnumerable<LinhaDeMontagem>> GetByFuncionarioId(int funcionarioId)
        {
            var parameters = new { IdFuncionario = funcionarioId };
            var result = await _db.LoadData<LinhaDeMontagem, dynamic>(
                storedProcedure: "spGetLinhasDeMontagemPorUtilizador",
                parameters: parameters
            );

            return result;
        }

        public async Task<IEnumerable<LinhaDeMontagem>> GetAll()
        {
            var result = await _db.LoadData<LinhaDeMontagem, dynamic>(
                storedProcedure: "spLinhaDeMontagem_GetAll",
                parameters: new { }
            );

            return result;
        }

        public async Task Insert(LinhaDeMontagem linha)
        {
            var parameters = new
            {
                linha.DataDeInicio,
                linha.DataDeFim,
                linha.Estado,
                linha.Satisfacao,
                linha.IdFuncionario,
                linha.IdProduto
            };

            await _db.SaveData("spLinhaDeMontagem_Insert", parameters);
        }

        public async Task Update(LinhaDeMontagem linha)
        {
            var parameters = new
            {
                linha.Id,
                linha.DataDeInicio,
                linha.DataDeFim,
                linha.Estado,
                linha.IdFuncionario,
                linha.IdProduto
            };

            await _db.SaveData("spLinhaDeMontagem_Update", parameters);
        }

        public async Task Delete(int id)
        {
            var parameters = new { Id = id };
            await _db.SaveData("spLinhaDeMontagem_Delete", parameters);
        }
    }
}

using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Interfaces;

namespace MontagemBelasPizzas.Data.Repositories.Produtos
{
    public class CompraRepository : OperacaoRepository
    {
        private readonly ISqlDataAccess _db;

        public CompraRepository(ISqlDataAccess db) : base(db)
        {
            _db = db;
        }

        public async Task Insert(Compra compra)
        {
            var parameters = new
            {
                compra.Quantidade,
                compra.ValorUnitario,
                compra.ValorTotal,
                compra.DataDaOperacao,
                compra.IdAdministrador,
                compra.IdIngrediente
            };

            await _db.SaveData("spCompra_Insert", parameters);
        }
    }
}

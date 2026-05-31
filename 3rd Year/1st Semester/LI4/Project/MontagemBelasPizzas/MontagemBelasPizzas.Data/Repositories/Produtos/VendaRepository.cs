using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Interfaces;

namespace MontagemBelasPizzas.Data.Repositories.Produtos
{
    public class VendaRepository : OperacaoRepository
    {
        private readonly ISqlDataAccess _db;

        public VendaRepository(ISqlDataAccess db) : base(db)
        {
            _db = db;
        }

        public async Task Insert(Venda venda)
        {
            var parameters = new
            {
                venda.Quantidade,
                venda.ValorUnitario,
                venda.ValorTotal,
                venda.DataDaOperacao,
                venda.IdAdministrador,
                venda.IdProduto
            };

            await _db.SaveData("spVenda_Insert", parameters);
        }
    }
}

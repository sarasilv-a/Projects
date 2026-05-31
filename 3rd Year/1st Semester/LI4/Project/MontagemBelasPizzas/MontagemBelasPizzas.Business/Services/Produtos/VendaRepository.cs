using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Repositories.Produtos;

namespace MontagemBelasPizzas.Business.Services.Produtos
{
    public class VendaService
    {
        private readonly VendaRepository _vendaRepository;

        public VendaService(VendaRepository vendaRepository)
        {
            _vendaRepository = vendaRepository;
        }

        public async Task CreateVenda(Venda venda)
        {
            await _vendaRepository.Insert(venda);
        }
    }
}

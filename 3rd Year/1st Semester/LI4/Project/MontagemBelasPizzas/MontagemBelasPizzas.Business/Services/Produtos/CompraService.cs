using MontagemBelasPizzas.Data.Entities.Produtos;
using MontagemBelasPizzas.Data.Repositories.Produtos;

namespace MontagemBelasPizzas.Business.Services.Produtos
{
    public class CompraService
    {
        private readonly CompraRepository _compraRepository;

        public CompraService(CompraRepository compraRepository)
        {
            _compraRepository = compraRepository;
        }

        public async Task CreateCompra(Compra compra)
        {
            await _compraRepository.Insert(compra);
        }
    }
}

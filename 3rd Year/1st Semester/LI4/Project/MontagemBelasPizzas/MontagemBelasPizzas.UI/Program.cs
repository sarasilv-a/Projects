using MontagemBelasPizzas.UI.Components;
using MontagemBelasPizzas.Business.Services.Produtos;
using MontagemBelasPizzas.Business.Services.Utilizadores;
using MontagemBelasPizzas.Data.Repositories.Produtos;
using MontagemBelasPizzas.Data.Repositories.Utilizadores;
using MontagemBelasPizzas.Data.Interfaces;
using MontagemBelasPizzas.Data;
using Microsoft.AspNetCore.Components.Server.ProtectedBrowserStorage;
using Microsoft.AspNetCore.Components.Authorization;
using MontagemBelasPizzas.UI.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Hosting.StaticWebAssets;
using MudBlazor;
using MudBlazor.Services;


var builder = WebApplication.CreateBuilder(args);

// Register dependencies
builder.Services.AddSingleton<ISqlDataAccess, SqlDataAccess>();

// Repositories
builder.Services.AddScoped<CompraRepository>();
builder.Services.AddScoped<VendaRepository>();
builder.Services.AddScoped<IngredienteRepository>();
builder.Services.AddScoped<LinhaDeMontagemRepository>();
builder.Services.AddScoped<MontagemRepository>();
builder.Services.AddScoped<ProdutoRepository>();
builder.Services.AddScoped<OperacaoRepository>();
builder.Services.AddScoped<UtilizadorRepository>();

// Services
builder.Services.AddScoped<CompraService>();
builder.Services.AddScoped<VendaService>();
builder.Services.AddScoped<IngredienteService>();
builder.Services.AddScoped<LinhaDeMontagemService>();
builder.Services.AddScoped<MontagemService>();
builder.Services.AddScoped<ProdutoService>();
builder.Services.AddScoped<OperacaoService>();
builder.Services.AddScoped<UtilizadorService>();

builder.Services.AddMudServices(config =>
{
    config.SnackbarConfiguration.PositionClass = Defaults.Classes.Position.BottomLeft;
    config.SnackbarConfiguration.PreventDuplicates = false;
    config.SnackbarConfiguration.NewestOnTop = false;
    config.SnackbarConfiguration.ShowCloseIcon = true;
    config.SnackbarConfiguration.VisibleStateDuration = 2000;
    config.SnackbarConfiguration.HideTransitionDuration = 150;
    config.SnackbarConfiguration.ShowTransitionDuration = 150;
    config.SnackbarConfiguration.SnackbarVariant = Variant.Filled;
});

StaticWebAssetsLoader.UseStaticWebAssets(builder.Environment, builder.Configuration);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();


// Authentication
builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath = "/"; // P�gina de login
        options.LogoutPath = "/logout"; // P�gina de logout
    });
builder.Services.AddScoped<AuthenticationStateProvider, CustomAuthenticationStateProvider>();
builder.Services.AddScoped<ProtectedLocalStorage>();
builder.Services.AddAuthenticationCore();
builder.Services.AddAuthorizationCore();
builder.Services.AddCascadingAuthenticationState();
builder.Services.AddMudServices();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();

app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();
app.UseAuthentication();
app.UseAntiforgery();

app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();

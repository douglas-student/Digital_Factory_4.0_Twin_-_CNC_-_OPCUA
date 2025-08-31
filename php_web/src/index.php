<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoramento de Fábrica 4.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <header class="bg-primary text-white text-center py-3">
        <h1>Monitoramento de Fábrica 4.0</h1>
    </header>

    <main class="container py-4">
        <div id="maquinas-container" class="row row-cols-1 row-cols-md-3 g-4">
            <div class="loading-message text-center">
                <h2>Aguardando dados do banco de dados...</h2>
                <p>A primeira inicialização pode levar alguns segundos.</p>
            </div>
        </div>
    </main>

    <footer class="bg-primary text-white text-center py-3 mt-4">
        <p>Projeto de Gêmeo Digital - Indústria 4.0</p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <script src="assets/js/update_dashboard.js"></script>
</body>
</html>
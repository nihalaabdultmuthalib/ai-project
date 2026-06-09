import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('postgresql://postgres:2271@localhost:5432/ai_qa')
    
    # Show tables
    rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    print('Connected to PostgreSQL!')
    print('Tables found:')
    for r in rows:
        print(f'  - {r["table_name"]}')
    
    # Insert a test row
    await conn.execute(
        "INSERT INTO document_chunks (source, content, embedding) VALUES ($1, $2, $3::jsonb)",
        'test_source', 'This is a test document chunk', '[0.1, 0.2, 0.3]'
    )
    print('Inserted test row!')
    
    # Read it back
    result = await conn.fetch('SELECT id, source, content FROM document_chunks')
    print('Data in table:')
    for r in result:
        print(f'  id={r["id"]} | source={r["source"]} | content={r["content"]}')
    
    await conn.close()
    print('Done!')

asyncio.run(test())

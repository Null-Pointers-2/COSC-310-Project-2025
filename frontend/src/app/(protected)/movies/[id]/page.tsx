export default function MovieDetailPage({ params }: { params: { id: string } }) {
  return <h1>Movie ID: {params.id}</h1>;
}

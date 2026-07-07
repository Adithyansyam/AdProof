export function BriefForm() {
  return (
    <form>
      <label>
        Brand Name
        <input type="text" name="brand_name" required />
      </label>
      <label>
        Brief
        <textarea name="brief_text" required />
      </label>
      <label>
        Reference Image (optional)
        <input type="file" name="reference_image" accept="image/*" />
      </label>
      <button type="submit">Create Brief</button>
    </form>
  );
}

class CreateMetrics < ActiveRecord::Migration
  def change
    create_table :metrics do |t|
      t.references :location, index: true, foreign_key: true
      t.string :name
      t.float :current

      t.timestamps null: false
    end
  end
end

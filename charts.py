
import matplotlib.pyplot as plt


def nutrient_chart(totals):
    nutrients = ["Proteins", "Carbs", "Fat", "Fibre"]
    values = [totals[name] for name in nutrients]

    fig, ax = plt.subplots()
    ax.bar(nutrients, values)

    ax.set_title("Nutrients Consumed Today")
    ax.set_ylabel("Amount (grams)")

    return fig
